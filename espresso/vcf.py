from . import search_regex, extract_sample_name

VCF_NAME_REGEX = '(?P<sample>.+?)(\\.\\w+?)?\\.g\\.vcf(\\.gz)?$'


def collect_vcf_files(directory, prefix=''):
    """
    Collect VCF and their index files
    :param directory: list of directories to search
    :param prefix: prepend to sample name
    :return: three lists of VCF files, VCF index files and sample names
    """

    vcf_files = search_regex(directory, '\\.g\\.vcf(\\.gz)?$')
    vcf_index_files = search_regex(directory, '\\.g\\.vcf(\\.gz)?\\.tbi$')

    vcf_len = len(vcf_files)
    index_len = len(vcf_index_files)

    if vcf_len == 0:
        raise Exception('VCF files not found in {}'.format(directory))

    if vcf_len != index_len:
        raise Exception('VCF and index files not even. VCF: {}, Index: {}'.format(vcf_len, index_len))

    vcf_files.sort()
    vcf_index_files.sort()
    sample_names = [prefix + extract_sample_name(f, VCF_NAME_REGEX) for f in vcf_files]

    return vcf_files, vcf_index_files, sample_names
