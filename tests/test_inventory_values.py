import hashlib
import importlib.util
import json
from pathlib import Path
import unittest
spec = importlib.util.spec_from_file_location('inventory_values', Path(__file__).resolve().parents[1]/'scripts/inventory_values.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

class InventoryValuesTests(unittest.TestCase):
    def test_generated_content_is_exact_and_digest_bound(self):
        content = json.dumps({'schemaVersion':1,'evidenceType':'declared-enrollment-selection','selections':{'local':[]}}).encode()+b'\n'
        result = module.values(content,'a'*40,'v2.4.0','local')['enrollmentInventory']
        self.assertEqual(result['content'].encode(),content)
        self.assertEqual(result['sha256'],hashlib.sha256(content).hexdigest())
        self.assertEqual(result['sourceCommit'],'a'*40)
        self.assertEqual(result['sourceTag'],'v2.4.0')

    def test_mutable_ref_or_wrong_selector_or_schema_fail(self):
        for commit, tag, selector in [('main','v2.4.0','local'),('a'*40,'latest','local'),('a'*40,'v2.4.0','../evil')]:
            with self.assertRaises(ValueError): module.values(b'{}',commit,tag,selector)
        with self.assertRaises(ValueError): module.values(b'{}','a'*40,'v2.4.0','local')
