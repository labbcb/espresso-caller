"""Espresso-Caller command line tool"""

from os import mkdir
from os.path import exists, abspath

import click

import espresso.workflows as workflows


@click.group()
def cli():
    """
    Automates execution of workflows for processing WES/WGS data

    Raw paired-end FASTQ or raw gVCF files are collected, together with resources files (b37 or hg38) to generate
    JSON file that is used as input for data processing workflows (haplotype-calling, JointGenotyping or both).
    It assumes that each directory containing FASTQ files is a library or batch.
    FASTQ file names must follow this pattern: (sample_name)_R?[12].fastq(.gz)?
    Input and resources files are checked before workflows are submitted to Cromwell server.
    Output files are collected writing them to destination directory.

    'variant-discovery' workflow executes all data processing steps: from raw FASTQs to unified VCF.
    It is also able to combine previous raw gVCF files when executing 'JointGenotyping' workflow.

    'haplotype-calling' workflow takes FASTQ files and their metadata as input (plus resources files) and run
    Broad Institute GATK workflows: convert FASTQ to uBAM; align sequences to reference genome; merge aligned
    with unmapped sequences to create ready-analysis BAM; validate BAM files; convert BAM files to CRAM format;
    and call variants generating one raw gVCF per sample.

    'JointGenotyping' workflows takes raw gVCF files and merge into a single unified VCF.
    """


@cli.command('all')
@click.option('--host', help='Cromwell server URL')
@click.option('--fastq', 'fastq_directories', required=True, multiple=True, type=click.Path(exists=True),
              help='Path to directory containing paired-end FASTQ files')
@click.option('--library', 'library_names', required=True, multiple=True,
              help='Library name. One value for each FASTQ directory path')
@click.option('--date', 'run_dates', required=True, multiple=True,
              help='Run date in ISO8601 format. One value for each FASTQ directory path')
@click.option('--platform', 'platform_name', required=True,
              help='Name of the sequencing platform. One value for each FASTQ directory path')
@click.option('--center', 'sequencing_center', required=True,
              help='Sequencing center name. One value for each FASTQ directory path')
@click.option('--disable_platform_unit', is_flag=True, default=False,
              help='Disable extraction of platform unit (PU) from FASTQ header')
@click.option('--reference', required=True, type=click.Path(exists=True),
              help='Path to directory containing reference files')
@click.option('--version', 'genome_version', required=True, type=click.Choice(['hg38', 'b37']),
              help='Version of reference files')
@click.option('--vcf', 'vcf_directories', multiple=True, type=click.Path(exists=True),
              help='Path to directory containing raw gVCF and their index files')
@click.option('--prefix', 'prefixes', multiple=True,
              help='Add prefix to sample names from raw gVCF directory. One value for each gVCF directory path')
@click.option('--sleep', 'sleep_time', default=300, type=click.INT,
              help='Time to sleep (in seconds) between each workflow status check')
@click.option('--dont_run', is_flag=True, default=False, show_default=True,
              help='Do not submit workflow to Cromwell. Just create destination directory and write JSON and WDL files')
@click.option('--move', is_flag=True, default=False,
              help='Move output files to destination directory instead of copying them')
@click.option('--gatk_path_override')
@click.option('--gotc_path_override')
@click.option('--samtools_path_override')
@click.option('--bwa_commandline_override')
@click.option('--fastq_bam_mem_gb', type=click.FLOAT)
@click.option('--align_mem_gb', type=click.FLOAT)
@click.option('--merge_bam_mem_gb', type=click.FLOAT)
@click.option('--mark_duplicates_mem_gb', type=click.FLOAT)
@click.option('--sort_mem_gb', type=click.FLOAT)
@click.option('--baserecalibrator_mem_gb', type=click.FLOAT)
@click.option('--aplly_bqsr_mem_gb', type=click.FLOAT)
@click.option('--haplotype_caller_mem_gb', type=click.INT)
@click.option('--merge_gvcfs_mem_gb', type=click.INT)
@click.option('--validate_bam_mem_gb', type=click.INT)
@click.option('--indels_variant_recalibrator_mem_gb', 'indels_mem_gb', type=click.FLOAT)
@click.option('--snps_variant_recalibrator_mem_gb', 'snps_mem_gb', type=click.FLOAT)
@click.option('--align_num_cpu', type=click.INT)
@click.argument('callset_name')
@click.argument('destination', type=click.Path())
def variant_discovery(
        host, fastq_directories, run_dates, library_names, platform_name,
        sequencing_center, disable_platform_unit, reference, genome_version,
        vcf_directories, prefixes, sleep_time, move, gatk_path_override,
        gotc_path_override, samtools_path_override, bwa_commandline_override, fastq_bam_mem_gb,
        align_mem_gb, merge_bam_mem_gb, mark_duplicates_mem_gb,
        sort_mem_gb, baserecalibrator_mem_gb, aplly_bqsr_mem_gb, haplotype_caller_mem_gb,
        indels_mem_gb, snps_mem_gb, dont_run, callset_name, align_num_cpu, merge_gvcfs_mem_gb,
        validate_bam_mem_gb, destination):
    """Run haplotype-calling and JointGenotyping workflows"""
    if not exists(destination):
        mkdir(destination)
    destination = abspath(destination)

    inputs = workflows.haplotype_calling_inputs(
        directories=fastq_directories,
        library_names=library_names,
        platform_name=platform_name,
        run_dates=run_dates,
        sequencing_center=sequencing_center,
        disable_platform_unit=disable_platform_unit,
        reference=reference,
        genome_version=genome_version,
        gatk_path_override=gatk_path_override,
        gotc_path_override=gotc_path_override,
        samtools_path_override=samtools_path_override,
        bwa_commandline_override=bwa_commandline_override,
        fastq_bam_mem_gb=fastq_bam_mem_gb,
        align_mem_gb=align_mem_gb,
        merge_bam_mem_gb=merge_bam_mem_gb,
        mark_duplicates_mem_gb=mark_duplicates_mem_gb,
        sort_mem_gb=sort_mem_gb,
        baserecalibrator_mem_gb=baserecalibrator_mem_gb,
        aplly_bqsr_mem_gb=aplly_bqsr_mem_gb,
        haplotype_caller_mem_gb=haplotype_caller_mem_gb,
        merge_gvcfs_mem_gb=merge_gvcfs_mem_gb,
        validate_bam_mem_gb=validate_bam_mem_gb,
        align_num_cpu=align_num_cpu)

    workflows.submit_workflow(
        host, 'haplotype-calling', genome_version, inputs, destination,
        sleep_time, dont_run, move)

    vcf_directories = list(vcf_directories)
    vcf_directories.append(destination)

    prefixes = list(prefixes)
    prefixes.append('')

    inputs = workflows.joint_discovery_inputs(
        vcf_directories, prefixes, reference, genome_version, callset_name,
        gatk_path_override, indels_mem_gb, snps_mem_gb)
    workflows.submit_workflow(
        host, 'joint-discovery', genome_version, inputs, destination,
        sleep_time, dont_run, move)


@cli.command('hc')
@click.option('--host', help='Cromwell server URL')
@click.option('--fastq', 'directories', required=True, multiple=True, type=click.Path(exists=True),
              help='Path to directory containing paired-end FASTQ files')
@click.option('--library', 'library_names', required=True, multiple=True,
              help='Library name. One value for each FASTQ directory path')
@click.option('--date', 'run_dates', required=True, multiple=True,
              help='Run date in ISO8601 format. One value for each FASTQ directory path')
@click.option('--platform', 'platform_name', required=True,
              help='Name of the sequencing platform. One value for each FASTQ directory path')
@click.option('--center', 'sequencing_center', required=True,
              help='Sequencing center name. One value for each FASTQ directory path')
@click.option('--disable_platform_unit', is_flag=True, default=False,
              help='Disable extraction of platform unit (PU) from FASTQ header')
@click.option('--reference', required=True, type=click.Path(exists=True),
              help='Path to directory containing reference files')
@click.option('--version', 'genome_version', required=True, type=click.Choice(['hg38', 'b37']),
              help='Version of reference files')
@click.option('--dont_run', is_flag=True, default=False, show_default=True,
              help='Do not submit workflow to Cromwell. Just create destination directory and write JSON and WDL files')
@click.option('--sleep', 'sleep_time', default=300, type=click.INT,
              help='Time to sleep (in seconds) between each workflow status check')
@click.option('--move', is_flag=True, default=False,
              help='Move output files to destination directory instead of copying them')
@click.option('--gatk_path_override')
@click.option('--gotc_path_override')
@click.option('--samtools_path_override')
@click.option('--bwa_commandline_override')
@click.option('--fastq_bam_mem_gb', type=click.FLOAT)
@click.option('--align_mem_gb', type=click.FLOAT)
@click.option('--merge_bam_mem_gb', type=click.FLOAT)
@click.option('--mark_duplicates_mem_gb', type=click.FLOAT)
@click.option('--sort_mem_gb', type=click.FLOAT)
@click.option('--baserecalibrator_mem_gb', type=click.FLOAT)
@click.option('--aplly_bqsr_mem_gb', type=click.FLOAT)
@click.option('--haplotype_caller_mem_gb', type=click.INT)
@click.option('--merge_gvcfs_mem_gb', type=click.INT)
@click.option('--validate_bam_mem_gb', type=click.INT)
@click.option('--align_num_cpu', type=click.INT)
@click.argument('destination', type=click.Path())
def haplotype_calling(
        host, directories, library_names, run_dates, platform_name,
        sequencing_center, disable_platform_unit, reference, genome_version,
        dont_run, sleep_time, move, gatk_path_override, gotc_path_override,
        samtools_path_override, bwa_commandline_override, fastq_bam_mem_gb, align_mem_gb,
        merge_bam_mem_gb, mark_duplicates_mem_gb, sort_mem_gb,
        baserecalibrator_mem_gb, aplly_bqsr_mem_gb, haplotype_caller_mem_gb, merge_gvcfs_mem_gb,
        validate_bam_mem_gb, align_num_cpu, destination):
    """Run only haplotype-calling workflow"""
    if not exists(destination):
        mkdir(destination)
    destination = abspath(destination)

    inputs = workflows.haplotype_calling_inputs(
        directories=directories,
        library_names=library_names,
        platform_name=platform_name,
        run_dates=run_dates,
        sequencing_center=sequencing_center,
        disable_platform_unit=disable_platform_unit,
        reference=reference,
        genome_version=genome_version,
        gatk_path_override=gatk_path_override,
        gotc_path_override=gotc_path_override,
        samtools_path_override=samtools_path_override,
        bwa_commandline_override=bwa_commandline_override,
        fastq_bam_mem_gb=fastq_bam_mem_gb,
        align_mem_gb=align_mem_gb,
        merge_bam_mem_gb=merge_bam_mem_gb,
        mark_duplicates_mem_gb=mark_duplicates_mem_gb,
        sort_mem_gb=sort_mem_gb,
        baserecalibrator_mem_gb=baserecalibrator_mem_gb,
        aplly_bqsr_mem_gb=aplly_bqsr_mem_gb,
        haplotype_caller_mem_gb=haplotype_caller_mem_gb,
        merge_gvcfs_mem_gb=merge_gvcfs_mem_gb,
        validate_bam_mem_gb=validate_bam_mem_gb,
        align_num_cpu=align_num_cpu)

    workflows.submit_workflow(
        host, 'haplotype-calling', genome_version, inputs,
        abspath(destination), sleep_time, dont_run, move)


@cli.command('joint')
@click.option('--host', help='Cromwell server URL')
@click.option('--vcf', 'directories', required=True, multiple=True, type=click.Path(exists=True),
              help='Path to directory containing raw gVCF and their index files')
@click.option('--prefix', 'prefixes', multiple=True,
              help='Add prefix to sample names from raw gVCF directory. One value for each gVCF directory path')
@click.option('--reference', required=True, type=click.Path(exists=True),
              help='Path to directory containing reference files')
@click.option('--version', 'genome_version', required=True, type=click.Choice(['hg38', 'b37']),
              help='Version of reference files')
@click.option('--dont_run', is_flag=True, default=False, show_default=True,
              help='Do not submit workflow to Cromwell. Just create destination directory and write JSON and WDL files')
@click.option('--sleep', 'sleep_time', default=300, type=click.INT,
              help='Time to sleep (in seconds) between each workflow status check')
@click.option('--move', is_flag=True, default=False,
              help='Move output files to destination directory instead of copying them')
@click.option('--gatk_path_override')
@click.option('--indels_variant_recalibrator_mem_gb', 'indels_mem_gb', type=click.FLOAT)
@click.option('--snps_variant_recalibrator_mem_gb', 'snps_mem_gb', type=click.FLOAT)
@click.argument('callset_name')
@click.argument('destination', type=click.Path())
def joint_genotyping(
        host, directories, prefixes, reference, genome_version, dont_run,
        sleep_time, move, gatk_path_override, indels_mem_gb, snps_mem_gb,
        callset_name, destination):
    """Run only JointGenotyping-gatk4 workflow"""
    if not exists(destination):
        mkdir(destination)
    destination = abspath(destination)

    inputs = workflows.joint_discovery_inputs(
        directories, prefixes, reference, genome_version, callset_name,
        gatk_path_override, indels_mem_gb, snps_mem_gb)
    workflows.submit_workflow(
        host, 'joint-discovery', genome_version, inputs, destination,
        sleep_time, dont_run, move)
