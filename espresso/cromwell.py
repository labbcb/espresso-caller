import requests
from urllib.parse import urljoin
from re import compile, match, IGNORECASE


def abort(host, workflow_id, api_version='v1'):
    """
    Abort a running workflow
    :param host: Cromwell server URL
    :param workflow_id: Workflow ID
    :param api_version: Cromwell API version
    :return: dict containing workflow ID and updated status
    """
    path = '/api/workflows/{version}/{id}/abort'.format(id=workflow_id, version=api_version)
    response = post(urljoin(host, path))
    if response.get('status') in ('fail', 'error'):
        raise Exception(response.get('message'))
    return response.get('status')


def status(host, workflow_id, api_version='v1'):
    """
    Retrieves the current state for a workflow
    :param host: Cromwell server URL
    :param workflow_id:
    :param api_version: Cromwell API version
    :return:
    """
    path = '/api/workflows/{version}/{id}/status'.format(id=workflow_id, version=api_version)
    response = get(urljoin(host, path))
    if response.get('status') in ('fail', 'error'):
        raise Exception(response.get('message'))
    return response.get('status')


def submit(host, workflow, inputs=None, options=None, dependencies=None, labels=None, language=None,
           language_version=None, root=None, hold=None, api_version='v1'):
    """
    Submit a workflow for execution
    :param host: Cromwell server URL
    :param workflow: Workflow source file path (or URL)
    :param inputs: JSON or YAML file path containing the inputs
    :param options: JSON file path containing configuration options for the execution of this workflow
    :param dependencies: ZIP file containing workflow source files that are used to resolve local imports
    :param labels: JSON file containing labels to apply to this workflow
    :param language: Workflow language (WDL or CWL)
    :param language_version: Workflow language version (draft-2, 1.0 for WDL or v1.0 for CWL)
    :param root: The root object to be run. Only necessary for CWL submissions containing multiple objects
    :param hold: Put workflow on hold upon submission. By default, it is taken as false
    :param api_version: Cromwell API version
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

    path = '/api/workflows/{version}'.format(version=api_version)
    response = post(urljoin(host, path), data)
    if response.get('status') in ('fail', 'error'):
        raise Exception(response.get('message'))
    return response.get('id')


def outputs(host, workflow_id, api_version='v1'):
    """
    Get the outputs for a workflow
    :param host: Cromwell server URL
    :param workflow_id:
    :param api_version: Cromwell API version
    :return:
    """
    path = '/api/workflows/{version}/{id}/outputs'.format(id=workflow_id, version=api_version)
    response = get(urljoin(host, path))
    if response.get('status') in ('fail', 'error'):
        raise Exception(response.get('message'))
    return response.get('outputs')


def get(url, data=None, raw_response_content=False):
    """
    GET API endpoint
    :param url: URL
    :param data: query parameters
    :param raw_response_content: return raw response content instead of parsing as JSON to dict
    :return: dic object or content of response in bytes
    """
    response = requests.get(url, params=data)
    return response.content if raw_response_content else response.json()


def patch(url, data, raw_response_content=False):
    """
    PATCH API endpoint
    :param url: URL
    :param data: data to send as body
    :param raw_response_content: return raw response content instead of parsing as JSON to dict
    :return: dic object or content of response in bytes
    """
    response = requests.patch(url, data=data)
    return response.content if raw_response_content else response.json()


def post(url, data=None, raw_response_content=False):
    """
    POST API endpoint
    :param url: URL
    :param data: multipart/form-data parameters
    :param raw_response_content: return raw response content instead of parsing as JSON to dict
    :return: dic object or content of response in bytes
    """
    response = requests.post(url, files=data)
    return response.content if raw_response_content else response.json()


def is_url(path):
    regex = compile(
        r'^(?:http|ftp)s?://(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'
        r'localhost|\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})(?::\d+)?(?:/?|[/?]\S+)$', IGNORECASE)

    return match(regex, path) is not None
