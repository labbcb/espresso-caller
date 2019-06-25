import sys
from math import floor


def generate_intervals_gatk(genome_sizes_file, window_size, destination=sys.stdout):
    """
    Creates genomic intervals in, 1-based GATK-style (chr:start-end)
    :param genome_sizes_file: file containing size of references (chr size)
    :param window_size: size of each genomic interval
    :param destination: file to write
    """

    with open(genome_sizes_file) as file:
        while True:
            line = file.readline().rstrip()
            if not line:
                break
            reference_name, size = line.split()
            size = int(size)

            n = floor(size / window_size)
            for i in range(n):
                chr_start = i * window_size + i + 1
                chr_end = i * window_size + window_size + i + 1
                destination.write('{}:{}-{}'.format(reference_name, chr_start, chr_end))

            chr_start = n * window_size + n + 1
            chr_end = size
            destination.write('{}:{}-{}'.format(reference_name, chr_start, chr_end))
