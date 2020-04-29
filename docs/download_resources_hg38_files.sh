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

wget -q -P ${DESTINATION} \
    https://storage.googleapis.com/gcp-public-data--broad-references/hg38/v0/Homo_sapiens_assembly38.dict \
    https://storage.googleapis.com/gcp-public-data--broad-references/hg38/v0/Homo_sapiens_assembly38.fasta \
    https://storage.googleapis.com/gcp-public-data--broad-references/hg38/v0/Homo_sapiens_assembly38.fasta.fai \
    https://storage.googleapis.com/gcp-public-data--broad-references/hg38/v0/Homo_sapiens_assembly38.fasta.64.alt \
    https://storage.googleapis.com/gcp-public-data--broad-references/hg38/v0/Homo_sapiens_assembly38.fasta.64.sa \
    https://storage.googleapis.com/gcp-public-data--broad-references/hg38/v0/Homo_sapiens_assembly38.fasta.64.amb \
    https://storage.googleapis.com/gcp-public-data--broad-references/hg38/v0/Homo_sapiens_assembly38.fasta.64.bwt \
    https://storage.googleapis.com/gcp-public-data--broad-references/hg38/v0/Homo_sapiens_assembly38.fasta.64.ann \
    https://storage.googleapis.com/gcp-public-data--broad-references/hg38/v0/Homo_sapiens_assembly38.fasta.64.pac \
    https://storage.googleapis.com/gcp-public-data--broad-references/hg38/v0/Homo_sapiens_assembly38.dbsnp138.vcf \
    https://storage.googleapis.com/gcp-public-data--broad-references/hg38/v0/Homo_sapiens_assembly38.dbsnp138.vcf.idx \
    https://storage.googleapis.com/gcp-public-data--broad-references/hg38/v0/Mills_and_1000G_gold_standard.indels.hg38.vcf.gz \
    https://storage.googleapis.com/gcp-public-data--broad-references/hg38/v0/Mills_and_1000G_gold_standard.indels.hg38.vcf.gz.tbi \
    https://storage.googleapis.com/gcp-public-data--broad-references/hg38/v0/Homo_sapiens_assembly38.known_indels.vcf.gz \
    https://storage.googleapis.com/gcp-public-data--broad-references/hg38/v0/Homo_sapiens_assembly38.known_indels.vcf.gz.tbi \
    https://storage.googleapis.com/gcp-public-data--broad-references/hg38/v0/wgs_evaluation_regions.hg38.interval_list \
    https://storage.googleapis.com/gcp-public-data--broad-references/hg38/v0/hg38.even.handcurated.20k.intervals \
    https://storage.googleapis.com/gcp-public-data--broad-references/hg38/v0/1000G_phase1.snps.high_confidence.hg38.vcf.gz \
    https://storage.googleapis.com/gcp-public-data--broad-references/hg38/v0/1000G_phase1.snps.high_confidence.hg38.vcf.gz.tbi \
    https://storage.googleapis.com/gcp-public-data--broad-references/hg38/v0/1000G_omni2.5.hg38.vcf.gz \
    https://storage.googleapis.com/gcp-public-data--broad-references/hg38/v0/1000G_omni2.5.hg38.vcf.gz.tbi \
    https://storage.googleapis.com/gcp-public-data--broad-references/hg38/v0/Axiom_Exome_Plus.genotypes.all_populations.poly.hg38.vcf.gz \
    https://storage.googleapis.com/gcp-public-data--broad-references/hg38/v0/Axiom_Exome_Plus.genotypes.all_populations.poly.hg38.vcf.gz.tbi \
    https://storage.googleapis.com/gcp-public-data--broad-references/hg38/v0/hapmap_3.3.hg38.vcf.gz \
    https://storage.googleapis.com/gcp-public-data--broad-references/hg38/v0/hapmap_3.3.hg38.vcf.gz.tbi \


mkdir ${DESTINATION}/scattered_calling_intervals

for i in $(seq -f "%02g" 1 50)
do
    mkdir ${DESTINATION}/scattered_calling_intervals/temp_00${i}_of_50
    URL="https://storage.googleapis.com/genomics-public-data/resources/broad/hg38/v0/scattered_calling_intervals/temp_00${i}_of_50/scattered.interval_list"
    wget -q -P ${DESTINATION}/scattered_calling_intervals/temp_00${i}_of_50 ${URL}
    echo "${DESTINATION}/scattered_calling_intervals/temp_00${i}_of_50/scattered.interval_list" >> ${DESTINATION}/hg38_wgs_scattered_calling_intervals.txt
done