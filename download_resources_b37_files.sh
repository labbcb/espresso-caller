#!/usr/bin/env bash

# USAGE bash download_resources_b37_files.sh full_path_destination
# From: https://console.cloud.google.com/storage/browser/gatk-legacy-bundles/b37

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
    https://storage.googleapis.com/gatk-legacy-bundles/b37/human_g1k_v37_decoy.dict.gz \
    https://storage.googleapis.com/gatk-legacy-bundles/b37/human_g1k_v37_decoy.fasta.gz \
    https://storage.googleapis.com/gatk-legacy-bundles/b37/human_g1k_v37_decoy.fasta.fai.gz \
    https://storage.googleapis.com/gatk-legacy-bundles/b37/human_g1k_v37_decoy.fasta.sa \
    https://storage.googleapis.com/gatk-legacy-bundles/b37/human_g1k_v37_decoy.fasta.amb \
    https://storage.googleapis.com/gatk-legacy-bundles/b37/human_g1k_v37_decoy.fasta.bwt \
    https://storage.googleapis.com/gatk-legacy-bundles/b37/human_g1k_v37_decoy.fasta.ann \
    https://storage.googleapis.com/gatk-legacy-bundles/b37/human_g1k_v37_decoy.fasta.pac \
    https://storage.googleapis.com/gatk-legacy-bundles/b37/dbsnp_138.b37.vcf.gz \
    https://storage.googleapis.com/gatk-legacy-bundles/b37/dbsnp_138.b37.vcf.idx.gz \
    https://storage.googleapis.com/gatk-legacy-bundles/b37/Mills_and_1000G_gold_standard.indels.b37.vcf.gz \
    https://storage.googleapis.com/gatk-legacy-bundles/b37/Mills_and_1000G_gold_standard.indels.b37.vcf.idx.gz \
    https://storage.googleapis.com/gatk-legacy-bundles/b37/1000G_phase1.indels.b37.vcf.gz \
    https://storage.googleapis.com/gatk-legacy-bundles/b37/1000G_phase1.indels.b37.vcf.idx.gz \
    https://storage.googleapis.com/gatk-legacy-bundles/b37/1000G_phase1.snps.high_confidence.b37.vcf.gz \
    https://storage.googleapis.com/gatk-legacy-bundles/b37/1000G_phase1.snps.high_confidence.b37.vcf.idx.gz \
    https://storage.googleapis.com/gatk-legacy-bundles/b37/1000G_omni2.5.b37.vcf.gz \
    https://storage.googleapis.com/gatk-legacy-bundles/b37/1000G_omni2.5.b37.vcf.idx.gz \
    https://storage.googleapis.com/gatk-legacy-bundles/b37/hapmap_3.3.b37.vcf.gz \
    https://storage.googleapis.com/gatk-legacy-bundles/b37/hapmap_3.3.b37.vcf.idx.gz

# genomic intervals
wget -P ${DESTINATION} \
    https://storage.googleapis.com/gatk-legacy-bundles/b37/wgs_calling_regions.v1.interval_list

gunzip ${DESTINATION}/*.gz

mkdir ${DESTINATION}/scattered_wgs_intervals

for i in $(seq -f "%02g" 1 50)
do
    mkdir ${DESTINATION}/scattered_wgs_intervals/temp_00${i}_of_50
    URL="https://storage.googleapis.com/gatk-legacy-bundles/b37/scattered_wgs_intervals/scatter-50/temp_00${i}_of_50/scattered.interval_list"
    wget -P ${DESTINATION}/scattered_wgs_intervals/temp_00${i}_of_50 ${URL}
    echo "${DESTINATION}/scattered_wgs_intervals/temp_00${i}_of_50/scattered.interval_list" >> ${DESTINATION}/wgs_scattered_calling_intervals.txt
done

# generate unpadded intervals file
wget -O- https://raw.githubusercontent.com/igvteam/igv/master/genomes/sizes/1kg_v37.chrom.sizes | head -n -2 > ${DESTINATION}/1kg_v37.chrom.sizes
python3 generate_intervals_gatk.py -w 200000 ${DESTINATION}/1kg_v37.chrom.sizes > ${DESTINATION}/unpadded_intervals_200k.b37.list

# generate bwa index
bwa index ${DESTINATION}/human_g1k_v37.fasta

# download axiom vcf
wget -P ${DESTINATION} \
    ftp://ftp.broadinstitute.org/pub/ExAC_release/release1/resources/Axiom_Exome_Plus.genotypes.all_populations.poly.vcf.gz
tabix ${DESTINATION}/Axiom_Exome_Plus.genotypes.all_populations.poly.vcf.gz

# Available resource files but required
# https://storage.googleapis.com/gatk-legacy-bundles/b37/human_g1k_v37.dict.gz
# https://storage.googleapis.com/gatk-legacy-bundles/b37/human_g1k_v37.fasta.gz
# https://storage.googleapis.com/gatk-legacy-bundles/b37/human_g1k_v37.fasta.fai.gz
# https://storage.googleapis.com/gatk-legacy-bundles/b37/human_g1k_v37_decoy.fasta.gdx
# https://storage.googleapis.com/gatk-legacy-bundles/b37/human_g1k_v37_decoy.fasta.flat
# https://storage.googleapis.com/gatk-legacy-bundles/b37/1000G_phase3_v4_20130502.sites.vcf.gz
# https://storage.googleapis.com/gatk-legacy-bundles/b37/1000G_phase3_v4_20130502.sites.vcf.idx
# https://storage.googleapis.com/gatk-legacy-bundles/b37/ExAC.r0.3.nonTCGA.sites.vep.b37.vcf.gz
# https://storage.googleapis.com/gatk-legacy-bundles/b37/dbsnp_138.b37.excluding_sites_after_129.vcf.gz
# https://storage.googleapis.com/gatk-legacy-bundles/b37/hapmap_3.3_b37_pop_stratified_af.vcf.gz
# https://storage.googleapis.com/gatk-legacy-bundles/b37/cosmic_v54_120711.b37.vcf
# https://storage.googleapis.com/gatk-legacy-bundles/b37/cosmic_v54_120711.b37.vcf.idx
# https://storage.googleapis.com/gatk-legacy-bundles/b37/dbsnp_138.b37.excluding_sites_after_129.vcf
# https://storage.googleapis.com/gatk-legacy-bundles/b37/dbsnp_138.b37.excluding_sites_after_129.vcf.idx
# https://storage.googleapis.com/gatk-legacy-bundles/b37/autosomes-1kg-minusNA12878-ALL.b37.vcf
# https://storage.googleapis.com/gatk-legacy-bundles/b37/Broad.human.exome.b37.interval_list.gz
# https://storage.googleapis.com/gatk-legacy-bundles/b37/wgs_calling_regions.v1.list