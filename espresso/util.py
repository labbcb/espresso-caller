from os import listdir
from os.path import join, basename
from re import compile, search, IGNORECASE


def search_regex(directory, regex):
    """
    Search files by regex in directory
    :param directory: list of file path
    :param regex: regex to search
    :return: list of files that match regex
    """
    files = listdir(directory)
    m = compile(regex)
    return [join(directory, file) for file in files if m.search(basename(file))]


def extract_sample_name(file, regex):
    """
    Extract sample name from FASTQ or VCF file name
    :param file: a single FASTQ or VCF file
    :param regex: regex pattern used to extract sample name
    :return: sample name
    """
    filename = basename(file)
    result = search(regex, filename, IGNORECASE)

    if not result:
        raise Exception('Unable to extract sample name from ' + filename)

    return result.group('sample')
