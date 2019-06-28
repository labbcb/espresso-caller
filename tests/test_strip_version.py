from unittest import TestCase

from wfauto.vcf import strip_version


class TestStripVersion(TestCase):
    def test_strip_version(self):
        self.assertEqual(strip_version('sample.b37', 'b37'), 'sample')
        self.assertEqual(strip_version('sample', 'hg38'), 'sample')
