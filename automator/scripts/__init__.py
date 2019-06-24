import itertools
import os
import shutil
from json import dump
from os.path import join, basename
from shutil import copyfile
from time import sleep

import click
from wftool.cromwell import CromwellClient

from automator.workflows import get_workflow_file


def submit_workflow(host, workflow, version, inputs, destination):
    """
    Copy workflow file into destination; write inputs JSON file into destination; submit workflow to Cromwell server;
    wait to complete; move output files to destination
    :param host: Cromwell server URL
    :param workflow: workflow name
    :param version: reference genome version
    :param inputs: dict containing inputs data
    :param destination: directory to write all files
    """
    inputs_file = join(destination, 'hc.{}.inputs.json'.format(version))
    with open(inputs_file, 'w') as file:
        dump(inputs, file)

    pkg_workflow_file = get_workflow_file(workflow)
    workflow_file = join(destination, basename(pkg_workflow_file))
    copyfile(pkg_workflow_file, workflow_file)

    if not host:
        host = 'http://localhost:8000'
    client = CromwellClient(host)
    workflow_id = client.submit(workflow_file, inputs_file)
    click.echo('Cromwell workflow id: ' + workflow_id, err=True)

    while True:
        status = client.status(workflow_id)
        if status != 'Submitted' and status != 'Running':
            click.echo('Workflow terminated: ' + status, err=True)
            break
        click.echo('Workflow status: ' + status, err=True, nl=False)
        sleep(600)

    if status != 'Succeed':
        exit(1)

    outputs = client.outputs(workflow_id)
    for task in outputs:
        if isinstance(outputs[task], str):
            files = [outputs[task]]
        elif any(isinstance(i, list) for i in outputs[task]):
            files = itertools.chain.from_iterable(outputs[task])
        else:
            files = outputs[task]

        for file in files:
            if os.path.exists(file):
                dest_file = os.path.join(destination, os.path.basename(file))
                shutil.move(file, dest_file)
            else:
                click.echo('File not found: ' + file, err=True)
