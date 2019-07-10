from json import load
from os import listdir
from os.path import join, basename
from re import compile
from re import search, IGNORECASE


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


def load_json_file(json_file):
    """
    Loads JSON file and return dict
    :param json_file: Path to JSON file
    :return: dict
    """
    with open(json_file) as file:
        return load(file)


def merge_dicts(*dict_args):
    """
    Given any number of dicts, shallow copy and merge into a new dict,
    precedence goes to key value pairs in latter dicts.
    """
    result = {}
    for dictionary in dict_args:
        result.update(dictionary)
    return result


def extract_sample_name(file, regex):
    """
    Extract sample name from FASTQ file name
    :param file: a single FASTQ or VCF file
    :param regex: regex pattern used to extract sample name
    :return: sample name
    """
    name = basename(file)
    result = search(regex, name, IGNORECASE)

    if not result:
        raise Exception('Unable to extract sample name from ' + name)

    return result.group('sample')


def is_valid_run_date(date):
    """
    Validates date in ISO8601 format according to BAM specification
    :param date: str to validate
    :return: True if valid and False if invalid
    """
    regex = r'^(\d{4})-?(1[0-2]|0[1-9])-?(3[01]|0[1-9]|[12][0-9])' \
            r'(T(2[0-3]|[01][0-9]):?[0-5][0-9]:?[0-5][0-9](Z|[+-][0-5][0-9]:?[0-5][0-9]))?$'
    return compile(regex).match(date)
