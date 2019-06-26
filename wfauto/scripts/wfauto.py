from os import mkdir
from os.path import exists, abspath

import click

from wfauto.intervals import generate_intervals_gatk
from wfauto.scripts import submit_workflow
from wfauto.workflows import haplotype_caller_inputs, joint_discovery_inputs


@click.group()
def cli():
    """
    Automates execution of workflows for processing WES/WGS data

    Raw paired-end FASTQ or raw gVCF files are collected, together with resources files (b37 or hg38) to generate
    JSON file that is used as input for data processing workflows (haplotype-calling, joint-discovery or both).
    All workflows are submitted to Cromwell server.
    Output files are collected writing them to destination directory.

    'haplotype-calling' workflow takes FASTQ files and their metadata as input (plus resources files) and run
    Broad Institute GATK workflows: convert FASTQ to uBAM; align sequences to reference genome; merge aligned
    with unmapped sequences to create ready-analysis BAM; validate BAM files; convert BAM files to CRAM format;
    and call variants generating one raw gVCF per sample.

    'joint-discovery' workflows takes raw gVCF files and merge into a single unified VCF.
    """
    pass


@cli.command()
@click.option('--host', help='Cromwell server URL')
@click.option('--fastq', required=True, multiple=True, type=click.Path(exists=True),
              help='Path to directory containing paired-end FASTQ files')
@click.option('--library', required=True, multiple=True,
              help='Library name. One value for all samples or one for each FASTQ directory path')
@click.option('--platform', required=True, multiple=True, help='Name of the sequencing platform')
@click.option('--date', required=True, multiple=True,
              help='Run date.  One value for all samples or one for each FASTQ directory path')
@click.option('--center', required=True, multiple=True,
              help='Sequencing center name.  One value for all samples or one for each FASTQ directory path')
@click.option('--reference', required=True, type=click.Path(exists=True),
              help='Path to directory containing reference files')
@click.option('--version', required=True, type=click.Choice(['hg38', 'b37']),
              help='Version of reference files')
@click.option('--batch_tsv_file', default='fastq_files.tsv', help='Batch TSV file name', show_default=True)
@click.option('--gatk_path_override')
@click.option('--gotc_path_override')
@click.option('--samtools_path_override')
@click.option('--bwa_commandline_override')
@click.argument('callset_name')
@click.argument('destination', type=click.Path())
def variant_discovery(host, fastq, library, platform, date, center, reference, version, callset_name,
                      gatk_path_override, gotc_path_override, samtools_path_override, bwa_commandline_override,
                      destination):
    """Run haplotype-calling and joint-discovery workflows"""
    haplotype_calling(host, fastq, library, date, platform, center, reference, version,
                      gatk_path_override, gotc_path_override, samtools_path_override, bwa_commandline_override,
                      destination)
    joint_discovery(host, destination, reference, version, gatk_path_override, callset_name, destination)


@cli.command()
@click.option('-w', '--window_size', type=click.INT, default=200000, show_default=True, help='Window size')
@click.argument('genome_sizes')
@click.argument('destination', default='-', type=click.File('w'))
def intervals(genome_sizes, window_size, destination):
    """Generate genomic intervals in GATK-style .list format"""
    generate_intervals_gatk(genome_sizes, window_size, destination)


@cli.command()
@click.option('--host', help='Cromwell server URL')
@click.option('--vcf', required=True, multiple=True, type=click.Path(exists=True),
              help='Path to directory containing raw gVCF and their index files')
@click.option('--reference', required=True, type=click.Path(exists=True),
              help='Path to directory containing reference files')
@click.option('--version', required=True, type=click.Choice(['hg38', 'b37']),
              help='Version of reference files')
@click.option('--gatk_path_override')
@click.argument('callset_name')
@click.argument('destination', type=click.Path())
def joint_discovery(host, vcf, reference, version, gatk_path_override, callset_name, destination):
    """Run only joint-discovery-gatk4 workflow"""
    destination = abspath(destination)
    if not exists(destination):
        mkdir(destination)

    inputs = joint_discovery_inputs(vcf, reference, version, callset_name, gatk_path_override)
    submit_workflow(host, 'joint-discovery', version, inputs, destination)


@cli.command()
@click.option('--host', help='Cromwell server URL')
@click.option('--fastq', required=True, multiple=True, type=click.Path(exists=True),
              help='Path to directory containing paired-end FASTQ files')
@click.option('--library', required=True, multiple=True,
              help='Library name. One value for all samples or one for each FASTQ directory path')
@click.option('--date', required=True, multiple=True,
              help='Run date.  One value for all samples or one for each FASTQ directory path')
@click.option('--platform', required=True, multiple=True, help='Name of the sequencing platform')
@click.option('--center', required=True, multiple=True,
              help='Sequencing center name.  One value for all samples or one for each FASTQ directory path')
@click.option('--reference', required=True, type=click.Path(exists=True),
              help='Path to directory containing reference files')
@click.option('--version', required=True, type=click.Choice(['hg38', 'b37']),
              help='Version of reference files')
@click.option('--gatk_path_override')
@click.option('--gotc_path_override')
@click.option('--samtools_path_override')
@click.option('--bwa_commandline_override')
@click.argument('destination', type=click.Path())
def haplotype_calling(host, fastq, library, date, platform, center, reference, version,
                      gatk_path_override, gotc_path_override, samtools_path_override, bwa_commandline_override,
                      destination):
    """Run only haplotype-calling workflow"""
    destination = abspath(destination)
    if not exists(destination):
        mkdir(destination)

    inputs = haplotype_caller_inputs(fastq, library, date, platform, center, reference, version,
                                     gatk_path_override, gotc_path_override, samtools_path_override,
                                     bwa_commandline_override)
    submit_workflow(host, 'haplotype-calling', version, inputs, destination)
