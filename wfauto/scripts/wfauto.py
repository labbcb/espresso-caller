from os import mkdir
from os.path import exists, abspath, join

import click

from wfauto.fastq import create_batch_tsv
from wfauto.intervals import generate_intervals_gatk
from wfauto.scripts import submit_workflow
from wfauto.vcf import collect_vcf_files
from wfauto.workflows import haplotype_caller_inputs, joint_discovery_inputs


@click.group()
def cli():
    """Automates execution of BIPMed-related workflows"""
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
@click.argument('callset_name')
@click.argument('destination', type=click.Path())
def automate(host, fastq, library, platform, date, center, batch_tsv_file, reference, version, callset_name,
             gatk_path_override, gotc_path_override, samtools_path_override, destination):
    """Create batch TSV file; submit haplotype-calling and joint-discovery workflows to Cromwell server"""
    destination = abspath(destination)
    if not exists(destination):
        mkdir(destination)

    batch_tsv_file = join(destination, batch_tsv_file)
    with open(batch_tsv_file, 'w') as file:
        create_batch_tsv(fastq, library, date, platform, center, file)

    inputs = haplotype_caller_inputs(batch_tsv_file, reference, version, gatk_path_override, gotc_path_override,
                                     samtools_path_override)
    submit_workflow(host, 'hc', version, inputs, destination)

    vcf_files, vcf_index_files, sample_names = collect_vcf_files(destination)
    inputs = joint_discovery_inputs(sample_names, callset_name, vcf_files, vcf_index_files, reference, version, gatk_path_override)

    submit_workflow(host, 'joint', version, inputs, destination)


@cli.command()
@click.option('--host', help='Cromwell server URL')
@click.option('--reference', required=True, type=click.Path(exists=True),
              help='Path to directory containing reference files')
@click.option('--version', required=True, type=click.Choice(['hg38', 'b37']),
              help='Version of reference files')
@click.option('--gatk_path_override')
@click.option('--gotc_path_override')
@click.option('--samtools_path_override')
@click.argument('batch_tsv_file', type=click.File())
@click.argument('destination', type=click.Path())
def automate_batch(host, batch_tsv_file, reference, version, callset_name, gatk_path_override, gotc_path_override,
                   samtools_path_override, destination):
    """Submit a batch TSV file for haplotype-calling and joint-discovery workflows to Cromwell server"""
    destination = abspath(destination)
    if not exists(destination):
        mkdir(destination)

    inputs = haplotype_caller_inputs(batch_tsv_file, reference, version, gatk_path_override, gotc_path_override,
                                     samtools_path_override)
    submit_workflow(host, 'hc', version, inputs, destination)

    vcf_files, vcf_index_files, sample_names = collect_vcf_files(destination)
    inputs = joint_discovery_inputs(sample_names, callset_name, vcf_files, vcf_index_files, reference, version, gatk_path_override)

    submit_workflow(host, 'joint', version, inputs, destination)


@cli.command()
@click.option('--fastq', required=True, multiple=True, type=click.Path(exists=True),
              help='Path to directory containing paired-end FASTQ files')
@click.option('--library', required=True, multiple=True,
              help='Library name. One value for all samples or one for each FASTQ directory path')
@click.option('--date', required=True, multiple=True,
              help='Run date.  One value for all samples or one for each FASTQ directory path')
@click.option('--platform', required=True, multiple=True, help='Name of the sequencing platform')
@click.option('--center', required=True, multiple=True,
              help='Sequencing center name.  One value for all samples or one for each FASTQ directory path')
@click.argument('batch_tsv_file', default='-', type=click.File('w'))
def batch_tsv(fastq, library, date, platform, center, batch_tsv_file):
    """Generate batch TSV file containing FASTQ file paths and metadata for 'bipmed-haplotype-calling' workflow"""
    create_batch_tsv(fastq, library, date, platform, center, batch_tsv_file)


@cli.command()
@click.option('-w', '--window_size', type=click.INT, default=200000, show_default=True, help='Window size')
@click.argument('genome_sizes')
@click.argument('destination', default='-', type=click.File('w'))
def intervals_list(genome_sizes, window_size, destination):
    """Generate genomic intervals in GATK-style .list format"""
    generate_intervals_gatk(genome_sizes, window_size, destination)


@cli.command()
@click.option('--host', help='Cromwell server URL')
@click.option('--vcf', required=True, multiple=True, type=click.Path(exists=True),
              help='Path to directory containing VCF and their index files')
@click.option('--reference', required=True, type=click.Path(exists=True),
              help='Path to directory containing reference files')
@click.option('--version', required=True, type=click.Choice(['hg38', 'b37']),
              help='Version of reference files')
@click.option('--gatk_path_override')
@click.argument('callset_name')
@click.argument('destination', type=click.Path())
def joint(host, vcf, reference, version, gatk_path_override, callset_name, destination):
    """Submit raw gVCF files to 'joint-discovery-gatk4-local' workflow to Cromwell Server"""
    destination = abspath(destination)
    if not exists(destination):
        mkdir(destination)

    vcf_files, vcf_index_files, sample_names = collect_vcf_files(vcf)
    inputs = joint_discovery_inputs(sample_names, callset_name, vcf_files, vcf_index_files, reference, version, gatk_path_override)

    submit_workflow(host, 'joint', version, inputs, destination)


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
@click.option('--batch_tsv_file', default='fastq_files.tsv', help='Batch TSV file name', show_default=True)
@click.option('--gatk_path_override')
@click.option('--gotc_path_override')
@click.option('--samtools_path_override')
@click.argument('destination', type=click.Path())
def hc(host, fastq, library, date, platform, center, reference, version, batch_tsv_file,
       gatk_path_override, gotc_path_override, samtools_path_override, destination):
    """Submit FASTQ files to 'bipmed-haplotype-calling' workflow to Cromwell server"""
    destination = abspath(destination)
    if not exists(destination):
        mkdir(destination)

    batch_tsv_file = join(destination, batch_tsv_file)
    with open(batch_tsv_file, 'w') as file:
        create_batch_tsv(fastq, library, date, platform, center, file)

    inputs = haplotype_caller_inputs(batch_tsv_file, reference, version, gatk_path_override, gotc_path_override,
                                     samtools_path_override)
    submit_workflow(host, 'hc', version, inputs, destination)


@cli.command()
@click.option('--reference', required=True, type=click.Path(exists=True),
              help='Path to directory containing genome reference and resource files')
@click.option('--version', required=True, type=click.Choice(['hg38', 'b37']), help='Version of reference genome')
@click.option('--gatk_path_override')
@click.option('--gotc_path_override')
@click.option('--samtools_path_override')
@click.argument('batch_tsv_file', type=click.File())
@click.argument('destination', type=click.Path())
def hc_batch(host, batch_tsv_file, reference, version, gatk_path_override, gotc_path_override, samtools_path_override,
             destination):
    """Submit a batch TSV file to 'bipmed-haplotype-calling' workflow to Cromwell server"""
    destination = abspath(destination)
    if not exists(destination):
        mkdir(destination)

    inputs = haplotype_caller_inputs(batch_tsv_file, reference, version, gatk_path_override, gotc_path_override,
                                     samtools_path_override)
    submit_workflow(host, 'hc', version, inputs, destination)
