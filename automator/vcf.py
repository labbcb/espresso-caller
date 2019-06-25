from automator import search_regex


def collect_vcf_files(directory):
    """
    Collect VCF and their index files
    :param directory: directory to search
    :return: two lists of VCF files and VCF index files
    """

    vcf_files = search_regex(directory, '\\.vcf(\\.gz)?')
    vcf_index_files = search_regex(directory, '\\.vcf(\\.gz)?\\.tbi')

    vcf_len = len(vcf_files)
    index_len = len(vcf_index_files)

    if vcf_len == 0:
        raise Exception('VCF files not found in {}'.format(directory))

    if vcf_len != index_len:
        raise Exception('VCF and index files not even. Forward: {}, Reverse: {}'.format(vcf_len, index_len))

    return vcf_files, vcf_index_files
