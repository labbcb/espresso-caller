from wfauto import search_regex, extract_sample_name

VCF_NAME_REGEX = '(?P<sample>.+)(\\.\\w)?\\.g\\.vcf(\\.gz)?$'


def collect_vcf_files(directories):
    """
    Collect VCF and their index files
    :param directories: list of directories to search
    :return: three lists of VCF files, VCF index files and sample names
    """

    all_vcf_files = []
    all_vcf_index_files = []
    all_sample_names = []
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
        all_sample_names.extend([extract_sample_name(f, VCF_NAME_REGEX) for f in vcf_files])

    return all_vcf_files, all_vcf_index_files, all_sample_names