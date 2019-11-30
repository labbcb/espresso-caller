from os.path import abspath, isfile, exists, join, basename
from zipfile import ZipFile

from pkg_resources import resource_filename

from espresso import load_json_file, is_valid_run_date
from espresso.fastq import collect_fastq_files, extract_platform_units
from espresso.references import collect_resources_files, check_intervals_files
from espresso.vcf import collect_vcf_files

WORKFLOW_FILES = {'haplotype-calling': 'workflows/haplotype-calling.wdl',
                  'joint-discovery': 'workflows/joint-discovery-gatk4-local.wdl',
                  'bam-to-cram': 'workflows/bam-to-cram.wdl',
                  'haplotypecaller-gvcf-gatk4': 'workflows/haplotypecaller-gvcf-gatk4.wdl',
                  'paired-fastq-to-unmapped-bam': 'workflows/paired-fastq-to-unmapped-bam.wdl',
                  'processing-for-variant-discovery-gatk4': 'workflows/processing-for-variant-discovery-gatk4.wdl',
                  'validate-bam': 'workflows/validate-bam.wdl'}

IMPORTS_FILES = {'haplotype-calling': ['bam-to-cram', 'haplotypecaller-gvcf-gatk4', 'paired-fastq-to-unmapped-bam',
                                       'processing-for-variant-discovery-gatk4', 'validate-bam']}


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
    if workflow not in WORKFLOW_FILES.keys():
        raise Exception('Workflow not found: ' + workflow)

    params_file = resource_filename(__name__, 'inputs/{}.params.json'.format(workflow))
    return load_json_file(params_file)


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


def haplotype_caller_inputs(directories, library_names, platform_name, run_dates, sequencing_center, reference,
                            genome_version, gatk_path_override=None, gotc_path_override=None,
                            samtools_path_override=None, bwa_commandline_override=None):
    """
    Create inputs for 'haplotype-calling' workflow
    :param directories:
    :param library_names:
    :param platform_name:
    :param run_dates:
    :param sequencing_center:
    :param reference:
    :param genome_version:
    :param gatk_path_override:
    :param gotc_path_override:
    :param samtools_path_override:
    :param bwa_commandline_override:
    :return:
    """

    inputs = load_params_file('haplotype-calling')
    inputs['HaplotypeCalling.ref_name'] = genome_version

    invalid_dates = [d for d in run_dates if not is_valid_run_date(d)]
    if len(invalid_dates) != 0:
        raise Exception('Invalid run date(s): ' + ', '.join(invalid_dates))

    directories = [directories] if isinstance(directories, str) else directories
    for i in range(len(directories)):
        forward_files, reverse_files, sample_names = collect_fastq_files(directories[i])
        inputs['HaplotypeCalling.sample_name'].extend(sample_names)
        inputs['HaplotypeCalling.fastq_1'].extend(forward_files)
        inputs['HaplotypeCalling.fastq_2'].extend(reverse_files)
        inputs['HaplotypeCalling.platform_unit'].extend(extract_platform_units(forward_files))

        num_samples = len(sample_names)
        inputs['HaplotypeCalling.library_name'].extend([library_names[i]] * num_samples)
        inputs['HaplotypeCalling.run_date'].extend([run_dates[i]] * num_samples)
        inputs['HaplotypeCalling.platform_name'].extend([platform_name] * num_samples)
        inputs['HaplotypeCalling.sequencing_center'].extend([sequencing_center] * num_samples)

    inputs.update(collect_resources_files(reference, 'haplotype-calling', genome_version))

    check_intervals_files(inputs['HaplotypeCalling.scattered_calling_intervals_list'])

    if gatk_path_override:
        if not isfile(gatk_path_override):
            raise Exception('GATK found not found: ' + gatk_path_override)
        inputs['HaplotypeCalling.gatk_path_override'] = abspath(gatk_path_override)
    if gotc_path_override:
        if not exists(gotc_path_override):
            raise Exception('GOTC found not found: ' + gotc_path_override)
        inputs['HaplotypeCalling.gotc_path_override'] = abspath(gotc_path_override) + '/'
    if samtools_path_override:
        if not isfile(samtools_path_override):
            raise Exception('Samtools found not found: ' + samtools_path_override)
        inputs['HaplotypeCalling.samtools_path_override'] = abspath(samtools_path_override)
    if bwa_commandline_override:
        inputs['HaplotypeCalling.bwa_commandline_override'] = bwa_commandline_override

    return inputs


def joint_discovery_inputs(directories, prefixes, reference, version, callset_name, gatk_path_override=None):
    """
    Create inputs for 'joint-discovery-gatk4-local' workflow
    :param directories:
    :param prefixes:
    :param reference:
    :param version:
    :param gatk_path_override:
    :param callset_name:
    :return:
    """

    inputs = load_params_file('joint-discovery')

    if len(directories) != len(prefixes):
        raise Exception("Number of directories {} and prefixes {} are uneven.".format(directories, prefixes))

    for directory, prefix in zip(directories, prefixes):
        vcf_files, vcf_index_files, sample_names = collect_vcf_files(directory, prefix)
        inputs['JointGenotyping.input_gvcfs'].extend(vcf_files)
        inputs['JointGenotyping.input_gvcfs_indices'].extend(vcf_index_files)
        inputs['JointGenotyping.sample_names'].extend(sample_names)

    inputs['JointGenotyping.callset_name'] = callset_name

    inputs.update(collect_resources_files(reference, 'joint-discovery', version))

    if gatk_path_override:
        if not isfile(gatk_path_override):
            raise Exception('GATK found not found: ' + gatk_path_override)
        inputs['JointGenotyping.gatk_path_override'] = abspath(gatk_path_override)

    return inputs
