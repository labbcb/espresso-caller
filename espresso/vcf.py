from os.path import abspath

from .util import search_regex, extract_sample_name


def collect_vcf_files(directory, prefix='', vcf_name_regex='(?P<sample>.+?)(\\.\\w+?)?\\.g\\.vcf(\\.gz)?$'):
    """
    Collect sample name and absolute path to VCF and its index file
    :param directory: list of directories to search
    :param prefix: prepend to sample name
    :param vcf_name_regex: regular expression to extract sample name from file name
    :return: three lists of sample names, VCF files, VCF index files
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
    sample_names = [prefix + extract_sample_name(f, vcf_name_regex) for f in vcf_files]

    return sample_names, [abspath(vcf) for vcf in vcf_files], [abspath(index) for index in vcf_index_files]
