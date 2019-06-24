from os import mkdir
from os.path import exists, abspath, join

import click

from automator.fastq import create_batch_tsv
from automator.intervals import generate_intervals_gatk
from automator.scripts import submit_workflow
from automator.workflows import haplotype_caller


@click.group()
def cli():
    """Automates execution of BIPMed-related workflows"""
    pass


@cli.command()
@click.option('--fastq', required=True, multiple=True, type=click.Path(exists=True),
              help='Path to directory containing paired-end FASTQ files')
@click.option('--library', required=True, multiple=True,
              help='Library name. One value for all samples or one for each FASTQ directory path')
@click.option('--date', required=True, multiple=True,
              help='Run date.  One value for all samples or one for each FASTQ directory path')
@click.option('--center', required=True, multiple=True,
              help='Sequencing center name.  One value for all samples or one for each FASTQ directory path')
@click.argument('batch_tsv', default='-', type=click.File())
def fastq_tsv(fastq, library, platform, center, sample_regex, platform_unit, batch_tsv):
    """Generate TSV file containing FASTQ file paths and metadata for 'bipmed-haplotype-calling` workflow"""
    create_batch_tsv(fastq, library, platform, center, sample_regex, platform_unit)


@cli.command()
@click.option('--host', show_default=True, help='Cromwell server URL')
@click.option('--fastq', required=True, multiple=True, type=click.Path(exists=True),
              help='Path to directory containing paired-end FASTQ files')
@click.option('--library', required=True, multiple=True,
              help='Library name. One value for all samples or one for each FASTQ directory path')
@click.option('--date', required=True, multiple=True,
              help='Run date.  One value for all samples or one for each FASTQ directory path')
@click.option('--center', required=True, multiple=True,
              help='Sequencing center name.  One value for all samples or one for each FASTQ directory path')
@click.option('--reference', required=True, type=click.Path(exists=True),
              help='Path to directory containing reference files')
@click.option('--version', required=True, type=click.Choice(['hg38', 'b37']),
              help='Version of reference files')
@click.option('--batch_tsv', default='fastq_files.tsv', help='Batch TSV file name', show_default=True)
@click.option('--gatk_path_override')
@click.option('--gotc_path_override')
@click.option('--samtools_path_override')
@click.argument('destination', type=click.Path())
def hc(host, fastq, library, platform, center, sample_regex, platform_unit, batch_tsv,
       reference, version,
       gatk_path_override, gotc_path_override, samtools_path_override,
       destination):
    """Submit FASTQ files to 'bipmed-haplotype-calling' workflow to Cromwell server"""

    destination = abspath(destination)
    if not exists(destination):
        mkdir(destination)

    batch_tsv_file = join(destination, batch_tsv)
    create_batch_tsv(fastq, library, platform, center, sample_regex, platform_unit)

    inputs = haplotype_caller(batch_tsv_file, reference, version, gatk_path_override, gotc_path_override,
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
def hc_batch(host, batch_tsv_file, reference, version,
             gatk_path_override, gotc_path_override, samtools_path_override,
             destination):
    """Submit a batch TSV file to 'bipmed-haplotype-calling' workflow to Cromwell server"""

    destination = abspath(destination)
    if not exists(destination):
        mkdir(destination)

    inputs = haplotype_caller(batch_tsv_file, reference, version, gatk_path_override, gotc_path_override,
                              samtools_path_override)
    submit_workflow(host, 'hc', version, inputs, destination)


@cli.command()
@click.option('-w', '--window_size', type=click.INT, default=200000, show_default=True, help='Window size')
@click.argument('genome_sizes')
def intervals_list(genome_sizes, window_size):
    """Generate genomic intervals in GATK-style .list format"""
    for interval in generate_intervals_gatk(genome_sizes, window_size):
        click.echo(interval)
