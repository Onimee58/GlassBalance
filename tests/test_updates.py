import unittest
from glassbalance.update_check import is_newer, latest_stable_release, parse_version

class UpdateTests(unittest.TestCase):
    def test_versions(self):
        self.assertTrue(is_newer('v0.3.0','0.2.0'))
        self.assertTrue(is_newer('0.3.0','0.3.0-beta.2'))
        self.assertTrue(is_newer('0.3.0-beta.2','0.3.0-beta.1'))
        self.assertFalse(is_newer('0.2.0','0.3.0'))
        self.assertFalse(is_newer('0.3.0-beta.1','0.3.0'))
        self.assertFalse(is_newer('v0.2.0','0.2.0'))
        with self.assertRaises(ValueError): parse_version('not a version')
    def test_release_validation(self):
        example={'tag_name':'v0.3.0','html_url':'https://github.com/Onimee58/GlassBalance/releases/tag/v0.3.0','draft':False,'prerelease':False}
        self.assertEqual(latest_stable_release(example)['version'],'v0.3.0')
        with self.assertRaises(ValueError): latest_stable_release({**example,'prerelease':True})
        with self.assertRaises(ValueError): latest_stable_release({**example,'html_url':'https://untrusted.example/path'})
if __name__=='__main__': unittest.main()
