from unittest import TestCase

from espresso import extract_sample_name
from espresso.vcf import VCF_NAME_REGEX


class TestExtract_sample_name(TestCase):
    def test_extract_sample_name(self):
        self.assertEqual("725_14", extract_sample_name("/home/benilton/bioinf/res/macrogen/batch1/725_14.b37.g.vcf.gz", VCF_NAME_REGEX))
        self.assertEqual("325_14", extract_sample_name("/home/benilton/bioinf/res/macrogen/batch1/325_14.b37.g.vcf.gz", VCF_NAME_REGEX))
