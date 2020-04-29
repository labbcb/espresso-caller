"""Workflow input JSON generation and workflow submssion"""

import shutil
from itertools import chain
from json import load, dump
from os.path import abspath, isfile, exists, join, basename
import re
from time import sleep
from zipfile import ZipFile
import sys

import click
from pkg_resources import resource_filename

from . import cromwell as cromwell
from .fastq import collect_fastq_files, extract_platform_units
from .references import collect_resources_files, check_intervals_files
from .vcf import collect_vcf_files

WORKFLOW_FILES = {
    'haplotype-calling': 'workflows/haplotype-calling.wdl',
    'joint-discovery': 'workflows/joint-discovery-gatk4-local.wdl',
    'bam-to-cram': 'workflows/bam-to-cram.wdl',
    'haplotypecaller-gvcf-gatk4': 'workflows/haplotypecaller-gvcf-gatk4.wdl',
    'paired-fastq-to-unmapped-bam': 'workflows/paired-fastq-to-unmapped-bam.wdl',
    'processing-for-variant-discovery-gatk4': 'workflows/processing-for-variant-discovery-gatk4.wdl',
    'validate-bam': 'workflows/validate-bam.wdl'}

IMPORTS_FILES = {
    'haplotype-calling': [
        'bam-to-cram', 'haplotypecaller-gvcf-gatk4', 'paired-fastq-to-unmapped-bam',
        'processing-for-variant-discovery-gatk4', 'validate-bam']}


def submit_workflow(host, workflow, genome_version, inputs, destination, sleep_time=300, dont_run=False, move=False):
    """
    Copy workflow file into destination; write inputs JSON file into destination;
    submit workflow to Cromwell server; wait to complete; and copy output files to destination
    :param host: Cromwell server URL
    :param workflow: workflow name
    :param genome_version: reference genome version
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

    inputs_file = join(
        destination, '{}.{}.inputs.json'.format(workflow, genome_version))
    with open(inputs_file, 'w') as file:
        dump(inputs, file, indent=4, sort_keys=True)

    click.echo('Inputs JSON file: ' + inputs_file, err=True)

    if dont_run:
        click.echo(
            'Workflow will not be submitted to Cromwell. See workflow files in ' + destination)
        exit()

    if not host:
        host = 'http://localhost:8000'
    workflow_id = cromwell.submit(
        host, workflow_file, inputs_file, dependencies=imports_file)

    click.echo('Workflow submitted to Cromwell Server ({})'.format(host), err=True)
    click.echo('Workflow id: ' + workflow_id, err=True)
    click.echo(
        'Starting {} workflow with reference genome version {}.. Ctrl-C to abort.'.format(
            workflow, genome_version),
        err=True)

    try:
        while True:
            sleep(sleep_time)
            status = cromwell.status(host, workflow_id)
            if status != 'Submitted' and status != 'Running':
                click.echo('Workflow terminated: ' + status, err=True)
                break
        if status != 'Succeeded':
            sys.exit(1)
    except KeyboardInterrupt:
        click.echo('Aborting workflow.')
        cromwell.abort(host, workflow_id)
        sys.exit(1)

    outputs = cromwell.outputs(host, workflow_id)
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


def get_workflow_file(workflow):
    """
    Return package path to workflow file
    :param workflow: Workflow name
    :return: path to workflow file
    """

    if workflow not in WORKFLOW_FILES.keys():
        raise Exception('Workflow not found: ' + workflow)

    return resource_filename(__name__, WORKFLOW_FILES.get(workflow))


def load_params_file(workflow):
    """
    Given a workflow load its inputs JSON file when exists
    :param workflow: workflow name
    :return: JSON file content as dict or an empty dict if file not found
    """
    if workflow not in WORKFLOW_FILES.keys():
        raise Exception('Workflow not found: ' + workflow)

    params_file = resource_filename(
        __name__, 'inputs/{}.params.json'.format(workflow))
    if not exists(params_file):
        return {}
    with open(params_file) as file:
        return load(file)


def zip_imports_files(workflow, dest_dir):
    """
    Zip WDL files and write in destination directory
    :param workflow: workflow name
    :param dest_dir: destination directory
    :return: path to zip file or None if workflow does not require sub-workflows
    """

    if workflow not in IMPORTS_FILES.keys():
        return None

    zip_file = join(dest_dir, workflow + '.imports.zip')
    with ZipFile(zip_file, 'w') as file:
        for sub_workflow in IMPORTS_FILES.get(workflow):
            workflow_file = get_workflow_file(sub_workflow)
            file.write(workflow_file, basename(workflow_file))

    return zip_file


def haplotype_calling_inputs(
        directories, library_names, platform_name, run_dates,
        sequencing_center, disable_platform_unit, reference, genome_version,
        gatk_path_override=None, gotc_path_override=None,
        samtools_path_override=None, bwa_commandline_override=None,
        align_mem_size_gb=None, merge_bam_mem_size_gb=None,
        mark_duplicates_mem_size_gb=None, sort_mem_size_gb=None,
        baserecalibrator_mem_size_gb=None, aplly_bqsr_mem_size_gb=None, align_num_cpu=None):
    """
    Create inputs for 'haplotype-calling' workflow
    :param directories:
    :param library_names:
    :param platform_name:
    :param run_dates:
    :param sequencing_center:
    :param disable_platform_unit:
    :param reference:
    :param genome_version:
    :param gatk_path_override:
    :param gotc_path_override:
    :param samtools_path_override:
    :param bwa_commandline_override:
    :param align_mem_size_gb:
    :param merge_bam_mem_size_gb:
    :param mark_duplicates_mem_size_gb:
    :param sort_mem_size_gb:
    :param baserecalibrator_mem_size_gb:
    :param aplly_bqsr_mem_size_gb:
    :param align_num_cpu:
    :return:
    """

    inputs = load_params_file('haplotype-calling')
    inputs['HaplotypeCalling.ref_name'] = genome_version

    invalid_dates = [d for d in run_dates if not is_valid_run_date(d)]
    if len(invalid_dates) != 0:
        raise Exception('Invalid run date(s): ' + ', '.join(invalid_dates))

    directories = [directories] if isinstance(
        directories, str) else directories
    for idx, directory in enumerate(directories):
        forward_files, reverse_files, sample_names = collect_fastq_files(
            directory)
        inputs['HaplotypeCalling.sample_name'] += sample_names
        inputs['HaplotypeCalling.fastq_1'] += forward_files
        inputs['HaplotypeCalling.fastq_2'] += reverse_files

        if disable_platform_unit:
            inputs['HaplotypeCalling.platform_unit'] += ["-"] * len(forward_files)
        else:
            inputs['HaplotypeCalling.platform_unit'] += extract_platform_units(forward_files)

        num_samples = len(sample_names)
        inputs['HaplotypeCalling.library_name'] += [library_names[idx]] * num_samples
        inputs['HaplotypeCalling.run_date'] += [run_dates[idx]] * num_samples
        inputs['HaplotypeCalling.platform_name'] += [platform_name] * num_samples
        inputs['HaplotypeCalling.sequencing_center'] += [sequencing_center] * num_samples

    inputs.update(collect_resources_files(
        reference, 'haplotype-calling', genome_version))
    check_intervals_files(
        inputs['HaplotypeCalling.scattered_calling_intervals_list'])

    if gatk_path_override:
        if not isfile(gatk_path_override):
            raise Exception('GATK found not found: ' + gatk_path_override)
        inputs['HaplotypeCalling.gatk_path_override'] = abspath(
            gatk_path_override)
    if gotc_path_override:
        if not exists(gotc_path_override):
            raise Exception('GOTC found not found: ' + gotc_path_override)
        inputs['HaplotypeCalling.gotc_path_override'] = abspath(
            gotc_path_override) + '/'
    if samtools_path_override:
        if not isfile(samtools_path_override):
            raise Exception('Samtools found not found: ' +
                            samtools_path_override)
        inputs['HaplotypeCalling.samtools_path_override'] = abspath(
            samtools_path_override)
    if bwa_commandline_override:
        inputs['HaplotypeCalling.bwa_commandline_override'] = bwa_commandline_override

    if align_mem_size_gb:
        inputs['HaplotypeCalling.align_mem_size_gb'] = align_mem_size_gb
    if merge_bam_mem_size_gb:
        inputs['HaplotypeCalling.merge_bam_mem_size_gb'] = merge_bam_mem_size_gb
    if mark_duplicates_mem_size_gb:
        inputs['HaplotypeCalling.mark_duplicates_mem_size_gb'] = mark_duplicates_mem_size_gb
    if sort_mem_size_gb:
        inputs['HaplotypeCalling.sort_mem_size_gb'] = sort_mem_size_gb
    if baserecalibrator_mem_size_gb:
        inputs['HaplotypeCalling.baserecalibrator_mem_size_gb'] = baserecalibrator_mem_size_gb
    if aplly_bqsr_mem_size_gb:
        inputs['HaplotypeCalling.aplly_bqsr_mem_size_gb'] = aplly_bqsr_mem_size_gb
    if align_num_cpu:
        inputs['HaplotypeCalling.align_num_cpu'] = align_num_cpu

    return inputs


def joint_discovery_inputs(
        directories, prefixes, reference, version, callset_name,
        gatk_path_override=None, indels_mem_size_gb=None, snps_mem_size_gb=None):
    """
    Create inputs for 'joint-discovery-gatk4-local' workflow
    :param directories:
    :param prefixes:
    :param reference:
    :param version:
    :param gatk_path_override:
    :param callset_name:
    :param indels_mem_size_gb:
    :param snps_mem_size_gb:
    :return:
    """

    inputs = load_params_file('joint-discovery')

    if len(directories) != len(prefixes):
        raise Exception("Number of directories {} and prefixes {} are uneven.".format(
            directories, prefixes))

    for directory, prefix in zip(directories, prefixes):
        sample_names, vcf_files, vcf_index_files = collect_vcf_files(
            directory, prefix)
        inputs['JointGenotyping.sample_names'] += sample_names
        inputs['JointGenotyping.input_gvcfs'] += vcf_files
        inputs['JointGenotyping.input_gvcfs_indices'] += vcf_index_files

    inputs['JointGenotyping.callset_name'] = callset_name

    inputs.update(collect_resources_files(
        reference, 'joint-discovery', version))

    if gatk_path_override:
        if not isfile(gatk_path_override):
            raise Exception('GATK found not found: ' + gatk_path_override)
        inputs['JointGenotyping.gatk_path_override'] = abspath(
            gatk_path_override)

    if indels_mem_size_gb:
        inputs['JointGenotyping.indels_variant_recalibrator_mem_size_gb'] = indels_mem_size_gb
    if snps_mem_size_gb:
        inputs['JointGenotyping.snps_variant_recalibrator_mem_size_gb'] = snps_mem_size_gb

    return inputs


def is_valid_run_date(date):
    """
    Validates date in ISO8601 format according to BAM specification
    :param date: str to validate
    :return: True if valid and False if invalid
    """
    regex = r'^(\d{4})-?(1[0-2]|0[1-9])-?(3[01]|0[1-9]|[12][0-9])' \
            r'(T(2[0-3]|[01][0-9]):?[0-5][0-9]:?[0-5][0-9](Z|[+-][0-5][0-9]:?[0-5][0-9]))?$'
    return re.compile(regex).match(date)
