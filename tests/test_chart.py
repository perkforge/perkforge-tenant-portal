"""Offline Helm and ownership guards; never contact a cluster."""
import os
from pathlib import Path
import subprocess
import unittest
import yaml
ROOT = Path(__file__).resolve().parents[1]
CHART = ROOT / 'bundles/portal/chart'
HELM = os.environ.get('HELM', 'helm')

class ChartTests(unittest.TestCase):
    def render(self, *overrides):
        return subprocess.run([HELM, 'template', 'home-portal', str(CHART), '--namespace', 'tenant-home-portal', *overrides], text=True, capture_output=True)

    def enabled(self, *extra):
        return self.render('--set', 'enabled=true', '--set', 'image.digest=sha256:' + 'a'*64,
                           '--set', 'portalOrigin=https://portal.example.invalid',
                           '--set', 'identity.issuer=https://identity.example.invalid/realms/home',
                           '--set', 'identity.clientId=fixture', '--set', 'identity.audience=fixture-api',
                           '--set', 'identity.existingSecret=fixture-secret', '--set', 'serviceAccount.name=fixture-runtime', *extra)

    def test_disabled_renders_nothing(self):
        result = self.render()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(list(yaml.safe_load_all(result.stdout)), [])
        self.assertIs(yaml.safe_load((CHART/'values.yaml').read_text())['enabled'], False)

    def test_approved_application_values_enable_exact_digest_with_required_inputs(self):
        values = ROOT / 'bundles/portal/values.yaml'
        result = self.render('-f', str(values))
        self.assertEqual(result.returncode, 0, result.stderr)
        deployment = next(o for o in yaml.safe_load_all(result.stdout) if o['kind'] == 'Deployment')
        self.assertEqual(deployment['spec']['template']['spec']['imagePullSecrets'], [{'name': 'portal-ghcr'}])
        pod = deployment['spec']['template']['spec']
        self.assertEqual(pod['hostAliases'], [{'ip':'10.43.163.193','hostnames':['keycloak.local-lab.test']}])
        self.assertEqual(pod['volumes'], [{'name':'identity-ca','configMap':{'name':'portal-identity-ca','items':[{'key':'ca.crt','path':'ca.crt'}]}}])
        container = pod['containers'][0]
        self.assertEqual(container['volumeMounts'], [{'name':'identity-ca','mountPath':'/etc/portal/identity-ca','readOnly':True}])
        self.assertIn({'name':'NODE_EXTRA_CA_CERTS','value':'/etc/portal/identity-ca/ca.crt'}, container['env'])
        image = deployment['spec']['template']['spec']['containers'][0]['image']
        self.assertEqual(image, 'ghcr.io/perkforge/perkforge-portal@sha256:2e07afbb31fd462911a365893d05796090883464560478bd70179466af5b17b7')

    def test_activation_requires_complete_approved_config(self):
        self.assertNotEqual(self.render('--set', 'enabled=true').returncode, 0)
        for key, value in [('image.digest','latest'), ('portalOrigin','http://portal.invalid'), ('identity.issuer','http://identity.invalid'), ('identity.existingSecret',''), ('serviceAccount.name',''), ('tenantSource','live')]:
            self.assertNotEqual(self.enabled('--set', f'{key}={value}').returncode, 0, key)

    def test_only_namespaced_application_objects_and_hardened_runtime(self):
        result = self.enabled()
        self.assertEqual(result.returncode, 0, result.stderr)
        objects = list(yaml.safe_load_all(result.stdout))
        self.assertFalse(yaml.safe_load((CHART/'Chart.yaml').read_text()).get('dependencies'))
        self.assertFalse((CHART/'crds').exists())
        self.assertFalse(any('helm.sh/hook' in o.get('metadata', {}).get('annotations', {}) for o in objects))
        self.assertEqual({o['kind'] for o in objects}, {'Deployment', 'Service'})
        self.assertTrue(all(o['metadata']['namespace'] == 'tenant-home-portal' for o in objects))
        deployment = next(o for o in objects if o['kind']=='Deployment')
        self.assertEqual(deployment['spec']['replicas'], 1)
        self.assertEqual(deployment['spec']['strategy']['type'], 'Recreate')
        pod = deployment['spec']['template']['spec']
        self.assertIs(pod['automountServiceAccountToken'], False)
        self.assertEqual(pod['serviceAccountName'], 'fixture-runtime')
        self.assertIs(pod['securityContext']['runAsNonRoot'], True)
        container = pod['containers'][0]
        self.assertIs(container['securityContext']['readOnlyRootFilesystem'], True)
        self.assertIs(container['securityContext']['allowPrivilegeEscalation'], False)
        self.assertEqual(container['securityContext']['capabilities']['drop'], ['ALL'])
        env = {x['name']: x for x in container['env']}
        self.assertEqual(env['TENANT_SOURCE']['value'], 'disabled')
        self.assertIn('secretKeyRef', env['OIDC_CLIENT_SECRET']['valueFrom'])
        self.assertEqual(container['resources']['limits']['memory'], '192Mi')
        service = next(o for o in objects if o['kind']=='Service')
        self.assertEqual(service['spec']['type'], 'ClusterIP')

    def test_application_has_no_platform_transport_or_routing_dependency(self):
        fleet = yaml.safe_load((ROOT / 'bundles/portal/fleet.yaml').read_text())
        self.assertEqual(fleet['helm']['valuesFiles'], ['values.yaml'])
        self.assertNotIn('valuesFrom', fleet['helm'])
        self.assertNotIn('defaultNamespace', fleet)
        self.assertNotIn('labels', fleet)
        result = self.enabled('--namespace', 'another-tenant')
        self.assertEqual(result.returncode, 0, result.stderr)
        objects = list(yaml.safe_load_all(result.stdout))
        self.assertTrue(all(o['metadata']['namespace'] == 'another-tenant' for o in objects))
        self.assertNotIn('platform.perkforge.io', result.stdout)
        self.assertNotIn('portal-platform-values', (ROOT / 'bundles/portal/fleet.yaml').read_text())
