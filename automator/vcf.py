from automator import search_regex


def collect_vcf_files(directories):
    """
    Collect VCF and their index files
    :param directories: list of directories to search
    :return: two lists of VCF files and VCF index files
    """

    all_vcf_files = []
    all_vcf_index_files = []
    for directory in directories:
        vcf_files = search_regex(directory, '\\.g\\.vcf(\\.gz)?$')
        vcf_index_files = search_regex(directory, '\\.g\\.vcf(\\.gz)?\\.tbi$')

        vcf_len = len(vcf_files)
        index_len = len(vcf_index_files)

        if vcf_len == 0:
            raise Exception('VCF files not found in {}'.format(directory))

        if vcf_len != index_len:
            raise Exception('VCF and index files not even. VCF: {}, Index: {}'.format(vcf_len, index_len))

        all_vcf_files.extend(vcf_files)
        all_vcf_index_files.extend(vcf_index_files)

    return all_vcf_files, all_vcf_index_files
