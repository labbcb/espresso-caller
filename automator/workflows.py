from automator.json import load_json_file
from automator.references import collect_reference_files
from pkg_resources import resource_filename

WORKFLOW_FILES = dict(hc='bipmed-haplotype-calling.wdl')
PARAMS_FILES = dict(hc='hc.params.json')
RUNTIME_FILES = dict(hc='hc.runtime.json')
PARAM_REF_NAME = 'BIPMedHaplotypeCalling.PreProcessingForVariantDiscovery_GATK4.ref_name'
PARAM_INPUT_FILE = 'BIPMedHaplotypeCalling.inputFile'
PARAMS_GATK_PATH = [
    "BIPMedHaplotypeCalling.ConvertPairedFastQsToUnmappedBamWf.gatk_path_override",
    "BIPMedHaplotypeCalling.PreProcessingForVariantDiscovery_GATK4.gatk_path_override",
    "BIPMedHaplotypeCalling.HaplotypeCallerGvcf_GATK4.gatk_path_override"
]
PARAM_GOTC_PATH = "BIPMedHaplotypeCalling.PreProcessingForVariantDiscovery_GATK4.gotc_path_override"
PARAM_SAMTOOLS_PATH = "BIPMedHaplotypeCalling.HaplotypeCallerGvcf_GATK4.samtools_path_override"

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

    params_file = resource_filename(__name__, PARAMS_FILES.get(workflow))
    return load_json_file(params_file)


def load_params_file(workflow):
    if workflow not in WORKFLOW_FILES.keys():
        raise Exception('Workflow not found: ' + workflow)

    params_file = resource_filename(__name__, PARAMS_FILES.get(workflow))
    return load_json_file(params_file)


def haplotype_caller(batch_tsv_file, reference, version, gatk_path_override=None, gotc_path_override=None,
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
        for param in PARAMS_GATK_PATH:
            runtime[param] = gatk_path_override
    if gotc_path_override:
        runtime[PARAM_GOTC_PATH] = gotc_path_override
    if samtools_path_override:
        runtime[PARAM_SAMTOOLS_PATH] = samtools_path_override


    return {**params, **references, **runtime}
