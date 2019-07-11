from os.path import isfile
from unittest import TestCase
from tempfile import mkdtemp
from espresso.workflows import zip_imports_files


class TestZipImportsFiles(TestCase):

    def test_zip_imports_files(self):
        temp_dir = mkdtemp()
        zip_file = zip_imports_files('haplotype-calling', temp_dir)
        self.assertTrue(isfile(zip_file))
