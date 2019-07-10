from unittest import TestCase

from wfauto.references import load_references
from wfauto.workflows import WORKFLOW_FILES


class TestLoadReferences(TestCase):

    def test_load_references(self):
        for workflow in WORKFLOW_FILES.keys():
            for version in ('b37', 'hg38'):
                self.assertIs(type(load_references(workflow, version)), list)
