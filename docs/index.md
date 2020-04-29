# Espresso-Caller

## Reproducible example

```bash
FASTQ_DIR=NA12878
REF_DIR=references/hg38
DATASET_NAME=NA12878
RESULT_DIR=results/hg38
GENOME_VERSION=hg38

espresso all \
    --fastq $FASTQ_DIR \
    --library Phase3 \
    --date 2015-07-30 \
    --platform Illumina \
    --center IGSR \
    --disable_platform_unit \
    --reference $REF_DIR \
    --version $GENOME_VERSION \
	--dont_run \
    $DATASET_NAME \
    $RESULT_DIR

espresso joint \
    --vcf $RESULT_DIR \
	--prefix "" \
    --reference $REF_DIR \
    --version $GENOME_VERSION \
	--dont_run \
    $DATASET_NAME \
    $RESULT_DIR
```

## Required resources files

[Broad References - Human genomics reference files used for sequencing analytics](https://console.cloud.google.com/marketplace/details/broad-institute/references).

## Container images

## Memory requirements

| Workflow                               | Task                               | Default GB | Argument                                   |
| -------------------------------------- | ---------------------------------- | ---------- | ------------------------------------------ |
| ConvertPairedFastQsToUnmappedBamWf     | PairedFastQsToUnmappedBAM          | 7          |                                            |
| ConvertPairedFastQsToUnmappedBamWf     | CreateFoFN                         |            |                                            |
| PreProcessingForVariantDiscovery_GATK4 | GetBwaVersion                      | 1          |                                            |
| PreProcessingForVariantDiscovery_GATK4 | SamToFastqAndBwaMem                | 14         | `--align_mem_size_gb`                      |
| PreProcessingForVariantDiscovery_GATK4 | MergeBamAlignment                  | 4          | `--merge_bam_mem_size_gb`                  |
| PreProcessingForVariantDiscovery_GATK4 | SortAndFixTags                     | 10         | `--sort_mem_size_gb`                       |
| PreProcessingForVariantDiscovery_GATK4 | MarkDuplicates                     | 7.5        | `--mark_duplicates_mem_size_gb`            |
| PreProcessingForVariantDiscovery_GATK4 | CreateSequenceGroupingTSV          | 2          |                                            |
| PreProcessingForVariantDiscovery_GATK4 | BaseRecalibrator                   | 6          | `--baserecalibrator_mem_size_gb`           |
| PreProcessingForVariantDiscovery_GATK4 | GatherBqsrReports                  | 4          |                                            |
| PreProcessingForVariantDiscovery_GATK4 | ApplyBQSR                          | 4          | `--aplly_bqsr_mem_size_gb`                 |
| PreProcessingForVariantDiscovery_GATK4 | GatherBamFiles                     | 3          |                                            |
| HaplotypeCallerGvcf_GATK4              | CramToBamTask                      | 15         |                                            |
| HaplotypeCallerGvcf_GATK4              | HaplotypeCaller                    | 7          |                                            |
| HaplotypeCallerGvcf_GATK4              | MergeGVCFs                         | 3          |                                            |
| ValidateBamsWf                         | ValidateBAM                        | 4          |                                            |
| BamToCram                              | ConvertBamToCram                   |            |                                            |
| JointGenotyping                        | GetNumberOfSamples                 | 1          |                                            |
| JointGenotyping                        | ImportGVCFs                        | 7          |                                            |
| JointGenotyping                        | GenotypeGVCFs                      | 7          |                                            |
| JointGenotyping                        | HardFilterAndMakeSitesOnlyVcf      | 3.5        |                                            |
| JointGenotyping                        | IndelsVariantRecalibrator          | 26         |`--indels_variant_recalibrator_mem_size_gb` |
| JointGenotyping                        | SNPsVariantRecalibratorCreateModel | 104        |                                            |
| JointGenotyping                        | SNPsVariantRecalibrator            | 3.5        |`--snps_variant_recalibrator_mem_size_gb`   |
| JointGenotyping                        | GatherTranches                     | 7          |                                            |
| JointGenotyping                        | ApplyRecalibration                 | 7          |                                            |
| JointGenotyping                        | GatherVcfs                         | 7          |                                            |
| JointGenotyping                        | CollectVariantCallingMetrics       | 7          |                                            |
| JointGenotyping                        | GatherMetrics                      | 7          |                                            |
| JointGenotyping                        | DynamicallyCombineIntervals        | 3          |                                            |
