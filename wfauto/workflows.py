from os.path import abspath, isfile, exists

from pkg_resources import resource_filename

from wfauto import load_json_file, is_valid_run_date
from wfauto.fastq import collect_fastq_files, extract_platform_units
from wfauto.references import collect_resources_files, check_intervals_files
from wfauto.vcf import collect_vcf_files, strip_version

WORKFLOW_FILES = {'haplotype-calling': 'haplotype-calling.wdl',
                  'joint-discovery': 'joint-discovery-gatk4-local.wdl'}


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

    params_file = resource_filename(__name__, '{}.params.json'.format(workflow))
    return load_json_file(params_file)


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


def joint_discovery_inputs(directories, reference, version, callset_name, gatk_path_override=None):
    """
    Create inputs for 'joint-discovery-gatk4-local' workflow
    :param directories:
    :param reference:
    :param version:
    :param gatk_path_override:
    :param callset_name:
    :return:
    """

    inputs = load_params_file('joint-discovery')

    directories = [directories] if isinstance(directories, str) else directories
    for directory in directories:
        vcf_files, vcf_index_files, sample_names = collect_vcf_files(directory)
        inputs['JointGenotyping.input_gvcfs'].extend(vcf_files)
        inputs['JointGenotyping.input_gvcfs_indices'].extend(vcf_index_files)
        inputs['JointGenotyping.sample_names'].extend([strip_version(s, version) for s in sample_names])

    inputs['JointGenotyping.callset_name'] = callset_name

    inputs.update(collect_resources_files(reference, 'joint-discovery', version))

    if gatk_path_override:
        if not isfile(gatk_path_override):
            raise Exception('GATK found not found: ' + gatk_path_override)
        inputs['JointGenotyping.gatk_path_override'] = abspath(gatk_path_override)

    return inputs
