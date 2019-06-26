from wfauto import load_json_file, merge_dicts
from wfauto.references import collect_reference_files
from pkg_resources import resource_filename
from os.path import abspath, isfile, exists

WORKFLOW_FILES = dict(hc='bipmed-haplotype-calling.wdl', joint='joint-discovery-gatk4-local.wdl')
PARAM_REF_NAME = 'BIPMedHaplotypeCalling.PreProcessingForVariantDiscovery_GATK4.ref_name'
PARAM_INPUT_FILE = 'BIPMedHaplotypeCalling.inputFile'
PARAMS_GATK_PATH = dict(hc=[
    "BIPMedHaplotypeCalling.ConvertPairedFastQsToUnmappedBamWf.gatk_path_override",
    "BIPMedHaplotypeCalling.PreProcessingForVariantDiscovery_GATK4.gatk_path_override",
    "BIPMedHaplotypeCalling.HaplotypeCallerGvcf_GATK4.gatk_path_override"
], joint='JointGenotyping.gatk_path_override')
PARAM_GOTC_PATH = "BIPMedHaplotypeCalling.PreProcessingForVariantDiscovery_GATK4.gotc_path_override"
PARAM_SAMTOOLS_PATH = "BIPMedHaplotypeCalling.HaplotypeCallerGvcf_GATK4.samtools_path_override"
PARAM_INPUT_GVCF = 'JointGenotyping.sample_names'
PARAM_INPUT_IDX = 'JointGenotyping.input_gvcfs_indices'
PARAM_CALLSET = 'JointGenotyping.callset_name'


def get_workflow_file(workflow):
    """
    Return package path to workflow file
    :param workflow: Workflow name
    :return: path to workflow file
    """

    if workflow not in WORKFLOW_FILES.keys():
        raise Exception('Workflow not found: ' + workflow)

    return resource_filename(__name__, WORKFLOW_FILES.get(workflow))


def load_runtime_file(workflow):
    if workflow not in WORKFLOW_FILES.keys():
        raise Exception('Workflow not found: ' + workflow)

    params_file = resource_filename(__name__, '{}.runtime.json'.format(workflow))
    return load_json_file(params_file)


def load_params_file(workflow):
    if workflow not in WORKFLOW_FILES.keys():
        raise Exception('Workflow not found: ' + workflow)

    params_file = resource_filename(__name__, '{}.params.json'.format(workflow))
    return load_json_file(params_file)


def haplotype_caller_inputs(batch_tsv_file, reference, version, gatk_path_override=None, gotc_path_override=None,
                            samtools_path_override=None):
    """
    Create inputs for 'bipmed-haplotype-calling' workflow
    :param batch_tsv_file:
    :param reference:
    :param version:
    :param gatk_path_override:
    :param gotc_path_override:
    :param samtools_path_override:
    :return:
    """

    references = collect_reference_files(reference, 'hc', version)

    params = load_params_file('hc')
    params[PARAM_REF_NAME] = version
    params[PARAM_INPUT_FILE] = batch_tsv_file

    runtime = load_runtime_file('hc')
    if gatk_path_override:
        for param in PARAMS_GATK_PATH.get('hc'):
            if not isfile(gatk_path_override):
                raise Exception('GATK found not found: ' + gatk_path_override)
            runtime[param] = abspath(gatk_path_override)
    if gotc_path_override:
        if not exists(gotc_path_override):
            raise Exception('GOTC found not found: ' + gotc_path_override)
        runtime[PARAM_GOTC_PATH] = abspath(gotc_path_override) + '/'
    if samtools_path_override:
        if not isfile(samtools_path_override):
            raise Exception('Samtools found not found: ' + samtools_path_override)
        runtime[PARAM_SAMTOOLS_PATH] = abspath(samtools_path_override)

    return merge_dicts(runtime, references, params)


def joint_discovery_inputs(callset_name, vcf_files, vcf_index_files, reference, version, gatk_path_override=None):
    """
    Create inputs for 'joint-discovery-gatk4-local' workflow
    :param callset_name:
    :param vcf_files:
    :param vcf_index_files:
    :param reference:
    :param version:
    :param gatk_path_override:
    :return:
    """

    references = collect_reference_files(reference, 'joint', version)

    params = load_params_file('joint')
    params[PARAM_INPUT_GVCF] = vcf_files
    params[PARAM_INPUT_IDX] = vcf_index_files
    params[PARAM_CALLSET] = callset_name

    runtime = load_runtime_file('joint')
    if gatk_path_override:
        if not isfile(gatk_path_override):
            raise Exception('GATK found not found: ' + gatk_path_override)
        runtime[PARAMS_GATK_PATH.get('joint')] = abspath(gatk_path_override)

    return merge_dicts(runtime, references, params)
