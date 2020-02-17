#!/usr/bin/env bash

# USAGE: access destination directory first

wget https://github.com/broadinstitute/gatk/releases/download/4.1.0.0/gatk-4.1.0.0.zip
unzip gatk-4.1.0.0.zip

wget https://github.com/samtools/htslib/releases/download/1.9/htslib-1.9.tar.bz2
tar xvf htslib-1.9.tar.bz2
cd htslib-1.9/
./configure
make
cd ..

wget https://github.com/samtools/samtools/releases/download/1.9/samtools-1.9.tar.bz2
tar xvf samtools-1.9.tar.bz2
cd samtools-1.9/
./configure --without-curses
make
cd ..

wget https://github.com/lh3/bwa/releases/download/v0.7.17/bwa-0.7.17.tar.bz2
tar xvf bwa-0.7.17.tar.bz2
cd bwa-0.7.17/
make
cd ..
cp bwa-0.7.17/bwa .

wget https://github.com/broadinstitute/picard/releases/download/2.20.1/picard.jar

# only required to generate unpadded intervals for b37 genome version
wget https://github.com/arq5x/bedtools2/releases/download/v2.28.0/bedtools

## Software version according to broadinstitute/genomes-in-the-cloud Docker image
## docker inspect broadinstitute/genomes-in-the-cloud:2.3.1-1512499786 | grep GOTC | sort -u | sed -e 's#GOTC_##' -e 's#^ *##'
## "BGZIP_VER": "1.3",
## "BWA_VER": "0.7.15.r1140",
## "GATK34_VER": "3.4-g3c929b0",
## "GATK35_VER": "3.5-0-g36282e4",
## "GATK36_VER": "3.6-44-ge7d1cd2",
## "GATK4_VER": "4.beta.5",
## "PICARD_VER": "1.1150",
## "SAMTOOLS_VER": "1.3.1",
## "SVTOOLKIT_VER": "2.00-1650",
## "TABIX_VER": "0.2.5_r1005"