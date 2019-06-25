from itertools import chain
from json import dump
from os.path import join, basename, exists
from shutil import copyfile
from time import sleep

import click
from wftool.cromwell import CromwellClient

from automator.workflows import get_workflow_file


def submit_workflow(host, workflow, version, inputs, destination, sleep_time=600):
    """
    Copy workflow file into destination; write inputs JSON file into destination;
    submit workflow to Cromwell server; wait to complete; and copy output files to destination
    :param host: Cromwell server URL
    :param workflow: workflow name
    :param version: reference genome version
    :param inputs: dict containing inputs data
    :param destination: directory to write all files
    :param sleep_time: time in seconds to sleep between workflow status check
    """
    inputs_file = join(destination, 'hc.{}.inputs.json'.format(version))
    with open(inputs_file, 'w') as file:
        dump(inputs, file, indent=4, sort_keys=True)

    pkg_workflow_file = get_workflow_file(workflow)
    workflow_file = join(destination, basename(pkg_workflow_file))
    copyfile(pkg_workflow_file, workflow_file)

    if not host:
        host = 'http://localhost:8000'
    client = CromwellClient(host)
    workflow_id = client.submit(workflow_file, inputs_file)
    click.echo('Cromwell workflow id: ' + workflow_id, err=True)

    try:
        while True:
            click.echo('Sleeping for {} seconds..'.format(sleep_time))
            sleep(sleep_time)
            status = client.status(workflow_id)
            if status != 'Submitted' and status != 'Running':
                click.echo('Workflow terminated: ' + status, err=True)
                break
            click.echo('Workflow status: ' + status, err=True)
        if status != 'Succeed':
            exit(1)
    except KeyboardInterrupt:
        click.echo('Aborting workflow.')
        client.abort(workflow_id)

    outputs = client.outputs(workflow_id)
    for output in outputs.values():
        if isinstance(output, str):
            files = [output]
        elif any(isinstance(i, list) for i in output):
            files = list(chain.from_iterable(output))
        else:
            files = output

        for file in files:
            if exists(file):
                destination_file = join(destination, basename(file))
                click.echo('Collecting file ', file)
                copyfile(file, destination_file)
            else:
                click.echo('File not found: ' + file, err=True)
