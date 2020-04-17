from unittest import TestCase

from espresso.util import extract_sample_name

VCF_NAME_REGEX = '(?P<sample>.+?)(\\.\\w+?)?\\.g\\.vcf(\\.gz)?$'


class TestExtractSampleName(TestCase):
    def test_extract_sample_name(self):
        self.assertEqual("725_14", extract_sample_name("/home/benilton/bioinf/res/macrogen/batch1/725_14.b37.g.vcf.gz", VCF_NAME_REGEX))
        self.assertEqual("325_14", extract_sample_name("/home/benilton/bioinf/res/macrogen/batch1/325_14.b37.g.vcf.gz", VCF_NAME_REGEX))
