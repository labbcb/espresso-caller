from os.path import exists
from unittest import TestCase
from espresso.workflows import get_workflow_file, WORKFLOW_FILES


class TestGetWorkflowFile(TestCase):

    def test_get_workflow_files(self):
        for workflow in WORKFLOW_FILES.keys():
            f = get_workflow_file(workflow)
            self.assertTrue(exists(f), 'file not found {}'.format(f))
