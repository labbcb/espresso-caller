from json import load
from os import scandir
from re import compile


def search_regex(directory, regex):
    """
    Search files by regex in directory
    :param directory: list of file path
    :param regex: regex to search
    :return: list of files that match regex
    """
    files = scandir(directory)
    m = compile(regex)
    return [file.path for file in files if m.search(file.name)]


def load_json_file(json_file):
    """
    Loads JSON file and return dict
    :param json_file: Path to JSON file
    :return: dict
    """

    load(json_file)
