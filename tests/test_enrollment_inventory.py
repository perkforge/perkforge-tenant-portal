import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
import yaml

ROOT = Path(__file__).resolve().parents[1]

class InventoryChartTests(unittest.TestCase):
    def render(self, content, **changes):
        inventory = dict(enabled=True, sourceCommit='a'*40, selector='local',
                         sha256=hashlib.sha256(content.encode()).hexdigest(), content=content)
        inventory.update(changes)
        values = dict(enabled=True, image=dict(digest='sha256:'+'b'*64),
                      portalOrigin='https://portal.example.invalid',
                      identity=dict(issuer='https://identity.example.invalid', clientId='fixture', audience='fixture', existingSecret='fixture'),
                      serviceAccount=dict(name='fixture'), enrollmentInventory=inventory)
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml') as f:
            yaml.safe_dump(values, f); f.flush()
            return subprocess.run(['helm','template','portal',str(ROOT/'bundles/portal/chart'),'--namespace','tenant-portal','-f',f.name],text=True,capture_output=True)

    def test_mount_exact_bytes_no_api_authority(self):
        content = json.dumps({'schemaVersion':1,'evidenceType':'declared-enrollment-selection','selections':{'local':[]}})+'\n'
        result = self.render(content)
        self.assertEqual(result.returncode,0,result.stderr)
        objects = list(yaml.safe_load_all(result.stdout))
        self.assertEqual({o['kind'] for o in objects},{'Deployment','Service','ConfigMap'})
        cm = next(o for o in objects if o['kind']=='ConfigMap')
        self.assertEqual(cm['data']['enrollment-inventory.json'],content)
        pod = next(o for o in objects if o['kind']=='Deployment')['spec']['template']['spec']
        self.assertIs(pod['automountServiceAccountToken'],False)
        self.assertIn({'name':'enrollment-inventory','mountPath':'/etc/portal/enrollment','readOnly':True},pod['containers'][0]['volumeMounts'])
        env = {e['name']:e.get('value') for e in pod['containers'][0]['env']}
        self.assertEqual(env['ENROLLMENT_SOURCE'],'gitops-configmap')
        self.assertEqual(env['ENROLLMENT_INVENTORY_SHA256'],hashlib.sha256(content.encode()).hexdigest())

    def test_invalid_pin_selector_digest_and_size_rejected(self):
        for changes in [dict(sourceCommit='main'),dict(selector='unknown'),dict(sha256='0'*64)]:
            self.assertNotEqual(self.render('{}',**changes).returncode,0)
        self.assertNotEqual(self.render('x'*131073).returncode,0)
