version 1.0
## HaplotypeCalling workflow - from paired-end FASTQ files to per-sample raw gVCF files
## Welliton de Souza - well309@gmail.com
import "paired-fastq-to-unmapped-bam.wdl" as PairedFastqToUnmappedBam
import "processing-for-variant-discovery-gatk4.wdl" as ProcessingForVariantDiscoveryGATK4
import "haplotypecaller-gvcf-gatk4.wdl" as HaplotypeCallerGvcfGATK4
import "validate-bam.wdl" as ValidateBams
import "bam-to-cram.wdl" as ConvertToCram

workflow HaplotypeCalling {

    input {            
        Array[String] sample_name
        String ref_name

        Array[File] fastq_1
        Array[File] fastq_2
        Array[String] library_name
        Array[String] platform_unit
        Array[String] run_date
        Array[String] platform_name
        Array[String] sequencing_center

        File ref_fasta
        File ref_fasta_index
        File ref_dict
        File ref_pac
        File ref_sa
        File ref_ann
        File ref_amb
        File ref_bwt
        File? ref_alt 

        File dbSNP_vcf
        File dbSNP_vcf_index
        Array[File] known_indels_sites_VCFs
        Array[File] known_indels_sites_indices

        File scattered_calling_intervals_list

        String? bwa_commandline_override

        String? gatk_docker_override
        String? gotc_docker_override
        String? python_docker_override
        String? gitc_docker_override

        String? gatk_path_override
        String? gotc_path_override
        String? samtools_path_override

        Float? align_mem_gb
        Float? merge_bam_mem_gb
        Float? mark_duplicates_mem_gb
        Float? sort_mem_gb
        Float? baserecalibrator_mem_gb
        Float? aplly_bqsr_mem_gb
        Float? fastq_bam_mem_gb
        Int? haplotype_caller_mem_gb
        Int? merge_gvcfs_mem_gb
        Float? validate_bam_mem_gb

        Int? align_num_cpu
    }

    scatter (idx in range(length(sample_name))) {
        call PairedFastqToUnmappedBam.ConvertPairedFastQsToUnmappedBamWf {
            input:
                sample_name = sample_name[idx],
                fastq_1 = fastq_1[idx],
                fastq_2 = fastq_2[idx],
                readgroup_name = sample_name[idx],
                library_name = library_name[idx],
                platform_unit = platform_unit[idx],
                run_date = run_date[idx],
                platform_name = platform_name[idx],
                sequencing_center = sequencing_center[idx],
                gatk_docker = gatk_docker_override,
                gatk_path = gatk_path_override,
                fastq_bam_mem_gb = fastq_bam_mem_gb
        }

        call ProcessingForVariantDiscoveryGATK4.PreProcessingForVariantDiscovery_GATK4 {
            input:
                sample_name = sample_name[idx],
                flowcell_unmapped_bams_list = ConvertPairedFastQsToUnmappedBamWf.unmapped_bam_list,
                unmapped_bam_suffix = ".bam",
                ref_name = ref_name,
                ref_fasta = ref_fasta,
                ref_fasta_index = ref_fasta_index,
                ref_dict = ref_dict,
                ref_pac = ref_pac,
                ref_sa = ref_sa,
                ref_ann = ref_ann,
                ref_amb = ref_amb,
                ref_bwt = ref_bwt,
                ref_alt = ref_alt,
                dbSNP_vcf = dbSNP_vcf,
                dbSNP_vcf_index = dbSNP_vcf_index,
                known_indels_sites_VCFs = known_indels_sites_VCFs,
                known_indels_sites_indices = known_indels_sites_indices,
                bwa_commandline = bwa_commandline_override,
                gatk_docker = gatk_docker_override,
                gatk_path = gatk_path_override,
                gotc_docker = gotc_docker_override,
                gotc_path = gotc_path_override,
                python_docker = python_docker_override,
                align_mem_gb = align_mem_gb,
                merge_bam_mem_gb = merge_bam_mem_gb,
                mark_duplicates_mem_gb = mark_duplicates_mem_gb,
                sort_mem_gb = sort_mem_gb,
                baserecalibrator_mem_gb = baserecalibrator_mem_gb,
                aplly_bqsr_mem_gb = aplly_bqsr_mem_gb,
                align_num_cpu = align_num_cpu
        }

        call HaplotypeCallerGvcfGATK4.HaplotypeCallerGvcf_GATK4 {
            input:
                input_bam = PreProcessingForVariantDiscovery_GATK4.analysis_ready_bam,
                input_bam_index = PreProcessingForVariantDiscovery_GATK4.analysis_ready_bam_index,
                ref_dict = ref_dict,
                ref_fasta = ref_fasta,
                ref_fasta_index = ref_fasta_index,
                scattered_calling_intervals_list = scattered_calling_intervals_list,
                gatk_docker = gatk_docker_override,
                gatk_path = gatk_path_override,
                gitc_docker = gitc_docker_override,
                samtools_path = samtools_path_override,
                haplotype_caller_mem_gb = haplotype_caller_mem_gb,
                merge_gvcfs_mem_gb = merge_gvcfs_mem_gb
        }
    }

    call ValidateBams.ValidateBamsWf {
        input:
            bam_array = PreProcessingForVariantDiscovery_GATK4.analysis_ready_bam,
            gatk_docker = gatk_docker_override,
            gatk_path = gatk_path_override,
            mem_gb = validate_bam_mem_gb
    }

    call ConvertToCram.BamToCram {
        input:
            array_bams = PreProcessingForVariantDiscovery_GATK4.analysis_ready_bam,
            ref_fasta = ref_fasta,
            gitc_docker_override = gitc_docker_override,
            samtools_path_override = samtools_path_override
    }

    output {
        Array[File] output_vcf = HaplotypeCallerGvcf_GATK4.output_vcf
        Array[File] output_vcf_index = HaplotypeCallerGvcf_GATK4.output_vcf_index
        Array[File] validation_reports = ValidateBamsWf.validation_reports
        Array[File] duplication_metrics = PreProcessingForVariantDiscovery_GATK4.duplication_metrics
        Array[File] bqsr_report = PreProcessingForVariantDiscovery_GATK4.bqsr_report
        Array[File] cram_files = BamToCram.cram_files
        Array[File] cram_index = BamToCram.cram_index
        Array[File] bam_files = PreProcessingForVariantDiscovery_GATK4.analysis_ready_bam
        Array[File] bam_index = PreProcessingForVariantDiscovery_GATK4.analysis_ready_bam_index
    }
}