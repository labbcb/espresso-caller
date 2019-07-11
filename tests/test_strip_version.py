import unittest

from espresso.vcf import strip_version


class TestStripVersion(unittest.TestCase):
    def test_strip_version(self):
        self.assertEqual(strip_version('sample.b37', 'b37'), 'sample')
        self.assertEqual(strip_version('sample', 'hg38'), 'sample')


if __name__ == '__main__':
    unittest.main()
