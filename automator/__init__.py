from json import load
from os import listdir
from re import compile
from os.path import join, basename


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

    load(json_file)
