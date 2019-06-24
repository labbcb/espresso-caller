## BIPMed workflow - from paired FASTQ files to GVCF file per sample
## Welliton de Souza - well309@gmail.com
## Input:
## - A single TSV file conainting one sample per line with the following collumns (in this order):
##    1. Sample name, (tag `SM`)
##    2. Absolute path to single FASTQ file (forward, R1)
##    3. Absolute path to single FASTQ file (reverse, R1)
##    4. Library name (e.g. `Macrogen-102_10`)
##    5. Platform unit (e.g. `HKKJNBBXX:2:CCTCTATC`)
##    6. Date of sequencing, run date (e.g. `2016-09-01T02:00:00+0200`)
##    7. Platform name (e.g. `Macrogen`)
##    8. Sequencing center (e.g. `BCB`)
## Outputs (one per sample):
## - GVCF file (and its index)
## - Duplication metrics file
## - BQRS report file
## - Aligned BAM file (and its index)
## - Unmapped BAM file (and its index)
import "https://raw.githubusercontent.com/gatk-workflows/seq-format-conversion/1.0.1/paired-fastq-to-unmapped-bam.wdl" as PairedFastqToUnmappedBam
import "https://raw.githubusercontent.com/gatk-workflows/gatk4-data-processing/1.1.0/processing-for-variant-discovery-gatk4.wdl" as ProcessingForVariantDiscoveryGATK4
import "https://raw.githubusercontent.com/gatk-workflows/gatk4-germline-snps-indels/1.1.1/haplotypecaller-gvcf-gatk4.wdl" as HaplotypeCallerGvcfGATK4

workflow BIPMedHaplotypeCalling {

    File inputFile

    Array[Array[String]] data = read_tsv(inputFile)

    scatter (fastqData in data) {

        call PairedFastqToUnmappedBam.ConvertPairedFastQsToUnmappedBamWf {
            input:
                readgroup_name = [fastqData[0]],
                sample_name = [fastqData[0]],
                fastq_1 = [fastqData[1]],
                fastq_2 = [fastqData[2]],
                library_name = [fastqData[3]],
                platform_unit = [fastqData[4]],
                run_date = [fastqData[5]],
                platform_name = [fastqData[6]],
                sequencing_center = [fastqData[7]],
                ubam_list_name = sub(basename(fastqData[0]), "_R1.fastq.gz", "_unmapped_bam")
        }

        call ProcessingForVariantDiscoveryGATK4.PreProcessingForVariantDiscovery_GATK4 {
            input:
              sample_name = sub(basename(fastqData[0]), "_R1.fastq.gz", ""),
              flowcell_unmapped_bams_list = ConvertPairedFastQsToUnmappedBamWf.unmapped_bam_list,
              unmapped_bam_suffix = ".bam"
        }

        call HaplotypeCallerGvcfGATK4.HaplotypeCallerGvcf_GATK4 {
            input:
                input_bam = PreProcessingForVariantDiscovery_GATK4.analysis_ready_bam,
                input_bam_index = PreProcessingForVariantDiscovery_GATK4.analysis_ready_bam_index
        }
    }

    output {
        Array[File] vcfFiles = HaplotypeCallerGvcf_GATK4.output_vcf
        Array[File] vcfIndexFiles = HaplotypeCallerGvcf_GATK4.output_vcf_index

        Array[File] duplicationMetricsFiles = PreProcessingForVariantDiscovery_GATK4.duplication_metrics
        Array[File] bqsrReportFiles = PreProcessingForVariantDiscovery_GATK4.bqsr_report
        Array[File] bamFiles = PreProcessingForVariantDiscovery_GATK4.analysis_ready_bam
        Array[File] bamIndexFiles = PreProcessingForVariantDiscovery_GATK4.analysis_ready_bam_index

        Array[Array[File]] unmappedBamFiles = ConvertPairedFastQsToUnmappedBamWf.output_bams
        Array[File] unmappedBamListFiles = ConvertPairedFastQsToUnmappedBamWf.unmapped_bam_list
    }

    meta {
        author: "Welliton Souza"
        email: "well309@gmail.com"
        workflow_version: "1.1.0"
    }
}