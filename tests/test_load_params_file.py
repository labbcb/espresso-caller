from unittest import TestCase
from wfauto.workflows import load_params_file, WORKFLOW_FILES


class TestLoadParamsFile(TestCase):

    def test_load_params_file(self):
        for workflow in WORKFLOW_FILES.keys():
            self.assertIs(type(load_params_file(workflow)), dict)
