from json import load

from pkg_resources import resource_filename
from os.path import isfile, join, abspath, exists


def join_list_mixed(x, sep=', '):
    """
    Given a mixed list with str and list element join into a single str
    :param x: list to be joined
    :param sep: str to be used as separator between elements
    :return: str
    """
    return sep.join([sep.join(y) if isinstance(y, list) else y for y in x])


class Reference:
    """Represents a resource file required by workflows"""

    def __init__(self, param, filename, path=None):
        """
        Creates a Reference
        :param param: full parameter name
        :param filename: file name
        :param path: absolute path to file
        """
        self.param = param
        self.filename = filename
        self.path = path


def load_references(workflow, version):
    """
    Loads reference-related inputs from internal JSON
    :param workflow: Workflow name
    :param version: Version of reference files
    :return: list of Reference
    """
    json_file = resource_filename(
        __name__, 'inputs/{}.{}.resources.json'.format(workflow, version))
    if not exists(json_file):
        return []
    with open(json_file) as file:
        references = load(file)
    return [Reference(param, filename) for param, filename in references.items()]


def check_intervals_files(intervals_file):
    """
    Checks if all intervals files listed in the combined intervals file exist
    :param intervals_file: file that has the list of intervals files
    :raise Exception if file not found
    """

    missing_files = []
    with open(intervals_file) as file:
        while True:
            line = file.readline().strip()
            if not line:
                break
            if not isfile(line):
                missing_files.append(line)
    if len(missing_files) != 0:
        raise Exception('Missing intervals files in {}:\n'.format(
            intervals_file) + '\n'.join(missing_files))


def collect_resources_files(reference_dir, workflow, version):
    """
    Search for reference files and update reference-related input dict
    :param reference_dir: Path of directory to search
    :param workflow: Workflow name
    :param version: Version of reference files
    :return: dict containing reference-related data updated with absolute path to files
    :raise Exception if file not found
    """

    references = load_references(workflow, version)
    for reference in references:
        if isinstance(reference.filename, list):
            files = [abspath(join(reference_dir, file))
                     for file in reference.filename]
            if all([isfile(file) for file in files]):
                reference.path = files
        else:
            file = abspath(join(reference_dir, reference.filename))
            if isfile(file):
                reference.path = file

    missing_references = [
        reference.filename for reference in references if reference.path is None]

    if len(missing_references) != 0:
        raise Exception('Missing resource files ' +
                        join_list_mixed(missing_references))

    return {r.param: r.path for r in references}
