#!/usr/bin/env bash

# USAGE bash download_resources_hg38_files.sh full_path_destination

if [[ "$#" -ne 1 ]]; then
    echo "Specify full path to destination directory"
    exit 1
fi

DESTINATION=$1

if [[ "${DESTINATION}" != /* ]]; then
    echo "Specify full path to destination directory"
    exit 1
fi

wget -P ${DESTINATION} \
    https://storage.cloud.google.com/genomics-public-data/resources/broad/hg38/v0/Homo_sapiens_assembly38.dict \
    https://storage.cloud.google.com/genomics-public-data/resources/broad/hg38/v0/Homo_sapiens_assembly38.fasta \
    https://storage.cloud.google.com/genomics-public-data/resources/broad/hg38/v0/Homo_sapiens_assembly38.fasta.fai \
    https://storage.cloud.google.com/genomics-public-data/resources/broad/hg38/v0/Homo_sapiens_assembly38.fasta.64.alt \
    https://storage.cloud.google.com/genomics-public-data/resources/broad/hg38/v0/Homo_sapiens_assembly38.fasta.64.sa \
    https://storage.cloud.google.com/genomics-public-data/resources/broad/hg38/v0/Homo_sapiens_assembly38.fasta.64.amb \
    https://storage.cloud.google.com/genomics-public-data/resources/broad/hg38/v0/Homo_sapiens_assembly38.fasta.64.bwt \
    https://storage.cloud.google.com/genomics-public-data/resources/broad/hg38/v0/Homo_sapiens_assembly38.fasta.64.ann \
    https://storage.cloud.google.com/genomics-public-data/resources/broad/hg38/v0/Homo_sapiens_assembly38.fasta.64.pac \
    https://storage.cloud.google.com/genomics-public-data/resources/broad/hg38/v0/Homo_sapiens_assembly38.dbsnp138.vcf \
    https://storage.cloud.google.com/genomics-public-data/resources/broad/hg38/v0/Homo_sapiens_assembly38.dbsnp138.vcf.idx \
    https://storage.cloud.google.com/genomics-public-data/resources/broad/hg38/v0/Mills_and_1000G_gold_standard.indels.hg38.vcf.gz \
    https://storage.cloud.google.com/genomics-public-data/resources/broad/hg38/v0/Mills_and_1000G_gold_standard.indels.hg38.vcf.gz.tbi \
    https://storage.cloud.google.com/genomics-public-data/resources/broad/hg38/v0/Homo_sapiens_assembly38.known_indels.vcf.gz \
    https://storage.cloud.google.com/genomics-public-data/resources/broad/hg38/v0/Homo_sapiens_assembly38.known_indels.vcf.gz.tbi \
    https://storage.cloud.google.com/broad-references/hg38/v0/wgs_evaluation_regions.hg38.interval_list \
    https://storage.cloud.google.com/broad-references/hg38/v0/hg38.even.handcurated.20k.intervals \
    https://storage.cloud.google.com/genomics-public-data/references/hg38/v0/Homo_sapiens_assembly38.haplotype_database.txt \
    https://storage.cloud.google.com/broad-references/hg38/v0/1000G_phase1.snps.high_confidence.hg38.vcf.gz \
    https://storage.cloud.google.com/broad-references/hg38/v0/1000G_phase1.snps.high_confidence.hg38.vcf.gz.tbi \
    https://storage.cloud.google.com/broad-references/hg38/v0/1000G_omni2.5.hg38.vcf.gz \
    https://storage.cloud.google.com/broad-references/hg38/v0/1000G_omni2.5.hg38.vcf.gz.tbi \
    https://storage.cloud.google.com/broad-references/hg38/v0/Axiom_Exome_Plus.genotypes.all_populations.poly.hg38.vcf.gz \
    https://storage.cloud.google.com/broad-references/hg38/v0/Axiom_Exome_Plus.genotypes.all_populations.poly.hg38.vcf.gz.tbi \
    https://storage.cloud.google.com/broad-references/hg38/v0/hapmap_3.3.hg38.vcf.gz \
    https://storage.cloud.google.com/broad-references/hg38/v0/hapmap_3.3.hg38.vcf.gz.tbi \
    https://storage.cloud.google.com/broad-references/hg38/v0/wgs_evaluation_regions.hg38.interval_list \
    https://storage.cloud.google.com/broad-references/hg38/v0/hg38.even.handcurated.20k.intervals \
    https://storage.cloud.google.com/genomics-public-data/references/hg38/v0/Homo_sapiens_assembly38.haplotype_database.txt


mkdir ${DESTINATION}/scattered_calling_intervals

for i in $(seq -f "%02g" 1 50)
do
    mkdir ${DESTINATION}/scattered_calling_intervals/temp_00${i}_of_50
    URL="https://storage.cloud.google.com/genomics-public-data/resources/broad/hg38/v0/scattered_calling_intervals/temp_00${i}_of_50/scattered.interval_list"
    wget -P ${DESTINATION}/scattered_calling_intervals/temp_00${i}_of_50 ${URL}
    echo "${DESTINATION}/scattered_calling_intervals/temp_00${i}_of_50/scattered.interval_list" >> ${DESTINATION}/hg38_wgs_scattered_calling_intervals.txt
done