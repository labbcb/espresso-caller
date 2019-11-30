import shutil
from itertools import chain
from json import dump
from os.path import join, basename, exists
from time import sleep

import click
from ..cromwell import CromwellClient
from ..workflows import get_workflow_file, zip_imports_files


def submit_workflow(host, workflow, version, inputs, destination, sleep_time=300, dont_run=False, move=False):
    """
    Copy workflow file into destination; write inputs JSON file into destination;
    submit workflow to Cromwell server; wait to complete; and copy output files to destination
    :param host: Cromwell server URL
    :param workflow: workflow name
    :param version: reference genome version
    :param inputs: dict containing inputs data
    :param destination: directory to write all files
    :param sleep_time: time in seconds to sleep between workflow status check
    :param dont_run: Do not submit workflow to Cromwell. Just create destination directory and write JSON and WDL files
    :param move: Move output files to destination directory instead of copying them.
    """

    pkg_workflow_file = get_workflow_file(workflow)
    workflow_file = join(destination, basename(pkg_workflow_file))
    shutil.copyfile(pkg_workflow_file, workflow_file)

    click.echo('Workflow file: ' + workflow_file, err=True)

    imports_file = zip_imports_files(workflow, destination)
    if imports_file:
        click.echo('Workflow imports file: ' + imports_file)

    inputs_file = join(destination, '{}.{}.inputs.json'.format(workflow, version))
    with open(inputs_file, 'w') as file:
        dump(inputs, file, indent=4, sort_keys=True)

    click.echo('Inputs JSON file: ' + inputs_file, err=True)

    if dont_run:
        click.echo('Workflow will not be submitted to Cromwell. See workflow files in ' + destination)
        exit()

    if not host:
        host = 'http://localhost:8000'
    client = CromwellClient(host)
    workflow_id = client.submit(workflow_file, inputs_file, dependencies=imports_file)

    click.echo('Workflow submitted to Cromwell Server ({})'.format(host), err=True)
    click.echo('Workflow id: ' + workflow_id, err=True)
    click.echo('Starting {} workflow with reference genome version {}.. Ctrl-C to abort.'.format(workflow, version),
               err=True)

    try:
        while True:
            sleep(sleep_time)
            status = client.status(workflow_id)
            if status != 'Submitted' and status != 'Running':
                click.echo('Workflow terminated: ' + status, err=True)
                break
        if status != 'Succeeded':
            exit(1)
    except KeyboardInterrupt:
        click.echo('Aborting workflow.')
        client.abort(workflow_id)
        exit(1)

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
                click.echo('Collecting file ' + file, err=True)
                if move:
                    shutil.move(file, destination_file)
                else:
                    shutil.copyfile(file, destination_file)
            else:
                click.echo('File not found: ' + file, err=True)
