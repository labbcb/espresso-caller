import gzip
from os.path import basename
from re import search, IGNORECASE

from automator import search_regex


def collect_fastq_files(directory):
    """
    Search for paired-end FASTQ files and check parity
    :param directory: Directory containing paired-end FASTQ files
    :return: two lists with paths to FASTQ files (forward, reverse)
    """
    forward_files = search_regex(directory, '_R?1\\.fastq(\\.gz)?')
    reverse_files = search_regex(directory, '_R?2\\.fastq(\\.gz)?')

    forward_len = len(forward_files)
    reverse_len = len(reverse_files)

    if forward_len == 0 or reverse_len == 0:
        raise Exception('FASTQ files not found in {}'.format(directory))

    if forward_len != reverse_len:
        raise Exception('FASTQ files not even. Forward: {}, Reverse: {}'.format(forward_len, reverse_len))

    return forward_files, reverse_files


def extract_sample_name(fastq_file, regex='(?P<sample>.+)_R?[12]\\.fastq(\\.gz)?$'):
    """
    Extract sample name from FASTQ file name
    :param fastq_file: a single FASTQ file
    :param regex: regex pattern used to extract sample name
    :return: sample name
    """
    name = basename(fastq_file)
    result = search(regex, name, IGNORECASE)

    if not result:
        raise Exception('Unable to extract sample name from ' + name)

    return result.group('sample')


def extract_platform_unit(fastq_file):
    """
    Extract platform unit from FASTQ header
    :param fastq_file: a single FASTQ file
    :return: list of str
    """
    if fastq_file[-3:] == '.gz':
        file = gzip.open(fastq_file, 'rt')
    else:
        file = open(fastq_file)
    try:
        header = file.readline()
        parts = header.split(':')
        return '{}.{}.{}'.format(parts[2], parts[3], parts[9])
    finally:
        file.close()


def create_batch_tsv(directories, library_names, run_dates, platform_names, sequencing_centers, destination):
    """
    Create TSV file containing absolute path to FASTQ files and their metadata
    :param directories: list of directories containing paired-end FASTQ files
    :param library_names: list of library names, one for each directory
    :param run_dates: list of run dates, one for each directory
    :param platform_names: Name of the sequencing platform
    :param sequencing_centers: list of sequencing center names, one for each directory
    :param destination: file to write data as TSV
    """

    for i in range(len(directories)):
        forward_files, reverse_files = collect_fastq_files(directories[i])
        sample_names = [extract_sample_name(f) for f in forward_files]
        platform_units = [extract_platform_unit(f) for f in forward_files]

        for j in range(len(sample_names)):
            destination.write('{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n'.format(sample_names[j],
                                                                      forward_files[j],
                                                                      reverse_files[j],
                                                                      library_names[i],
                                                                      platform_units[j],
                                                                      run_dates[i],
                                                                      platform_names[i],
                                                                      sequencing_centers[i]))
