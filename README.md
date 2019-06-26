# Automates execution of workflows for processing WES/WGS data

Raw paired-end FASTQ or raw gVCF files are collected, together with resources files (b37 or hg38) to generate
JSON file that is used as input for data processing workflows (haplotype-calling, joint-discovery or both).
All workflows are submitted to Cromwell server.
Output files are collected writing them to destination directory.

'haplotype-calling' workflow takes FASTQ files and their metadata as input (plus resources files) and run
Broad Institute GATK workflows: convert FASTQ to uBAM; align sequences to reference genome; merge aligned
with unmapped sequences to create ready-analysis BAM; validate BAM files; convert BAM files to CRAM format;
and call variants generating one raw gVCF per sample.

'joint-discovery' workflows takes raw gVCF files and merge into a single unified VCF.
    
