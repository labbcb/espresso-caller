from . import is_url
from .client import Client


class CromwellClient(Client):
    """
    Cromwell API client.
    Provides all methods available of this API
    """

    def __init__(self, host, api_version='v1'):
        """
        Initializes CromwellClient
        :param host: Cromwell server URL
        :param api_version: Cromwell API version
        """
        super().__init__(host)
        self.api_version = api_version

    def abort(self, workflow_id):
        """
        Abort a running workflow
        :param workflow_id: Workflow ID
        :return: dict containing workflow ID and updated status
        """
        path = '/api/workflows/{version}/{id}/abort'.format(id=workflow_id, version=self.api_version)
        response = super().post(path)
        if response.get('status') in ('fail', 'error'):
            raise Exception(response.get('message'))
        return response.get('status')

    def status(self, workflow_id):
        """
        Retrieves the current state for a workflow
        :param workflow_id:
        :return:
        """
        path = '/api/workflows/{version}/{id}/status'.format(id=workflow_id, version=self.api_version)
        response = super().get(path)
        if response.get('status') in ('fail', 'error'):
            raise Exception(response.get('message'))
        return response.get('status')

    def submit(self, workflow, inputs=None, options=None, dependencies=None, labels=None, language=None,
               language_version=None, root=None, hold=None):
        """
        Submit a workflow for execution
        :param workflow: Workflow source file path (or URL)
        :param inputs: JSON or YAML file path containing the inputs
        :param options: JSON file path containing configuration options for the execution of this workflow
        :param dependencies: ZIP file containing workflow source files that are used to resolve local imports
        :param labels: JSON file containing labels to apply to this workflow
        :param language: Workflow language (WDL or CWL)
        :param language_version: Workflow language version (draft-2, 1.0 for WDL or v1.0 for CWL)
        :param root: The root object to be run. Only necessary for CWL submissions containing multiple objects
        :param hold: Put workflow on hold upon submission. By default, it is taken as false
        :return:
        """
        data = dict(workflowRoot=root, workflowOnHold=hold, workflowType=language, workflowTypeVersion=language_version)
        if is_url(workflow):
            data['workflowUrl'] = workflow
        else:
            data['workflowSource'] = open(workflow, 'rb')

        if inputs is not None:
            data['workflowInputs'] = open(inputs, 'rb')

        if dependencies is not None:
            data['workflowDependencies'] = open(dependencies, 'rb')
        if options is not None:
            data['workflowOptions'] = open(options, 'rb')
        if labels is not None:
            data['labels'] = open(labels, 'rb')

        path = '/api/workflows/{version}'.format(version=self.api_version)
        response = super().post(path, data)
        if response.get('status') in ('fail', 'error'):
            raise Exception(response.get('message'))
        return response.get('id')

    def outputs(self, workflow_id):
        """
        Get the outputs for a workflow
        :return:
        """
        path = '/api/workflows/{version}/{id}/outputs'.format(id=workflow_id, version=self.api_version)
        response = super().get(path)
        if response.get('status') in ('fail', 'error'):
            raise Exception(response.get('message'))
        return response.get('outputs')
