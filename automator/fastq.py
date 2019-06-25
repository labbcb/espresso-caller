from operator import itemgetter
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
    (zcat ${file} | head -n 1 | cut -f3,4,10 -d: | sed 's/:/./g')
    :param fastq_file: a single FASTQ file
    :return: list of str
    """
    with open(fastq_file) as file:
        return '.'.join(itemgetter(*file.readline().split(':'))([3, 4, 10]))


# 1. Sample name, (tag `SM`)
# 2. Absolute path to single FASTQ file (forward, R1)
# 3. Absolute path to single FASTQ file (reverse, R1)
# 4. Library name (e.g. `Macrogen-102_10`)
# 5. Platform unit (e.g. `HKKJNBBXX:2:CCTCTATC`)
# 6. Date of sequencing, run date (e.g. `2016-09-01T02:00:00+0200`)
# 7. Platform name (e.g. `Illumina`)
# 8. Sequencing center (e.g. `BCB`)
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

    for idx in range(len(directories)):
        forward_files, reverse_files = collect_fastq_files(directories[idx])
        sample_names = [extract_sample_name(f) for f in forward_files]
        platform_units = [extract_platform_unit(f) for f in forward_files]

        with open(destination, 'w') as file:
            for sample, forward, reverse, platform_unit in sample_names, forward_files, reverse_files, platform_units:
                file.write('{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}'.format(sample, forward, reverse, library_names[idx],
                                                                   platform_unit, run_dates[idx], platform_names[idx],
                                                                   sequencing_centers[idx]))
