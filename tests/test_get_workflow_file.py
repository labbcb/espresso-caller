from os.path import isfile
from unittest import TestCase
from wfauto.workflows import get_workflow_file, WORKFLOW_FILES


class TestGetWorkflowFile(TestCase):

    def test_get_workflow_files(self):
        for workflow in WORKFLOW_FILES.keys():
            self.assertTrue(isfile(get_workflow_file(workflow)))
