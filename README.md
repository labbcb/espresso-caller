# Automates genomic data processing

Working with Workflow Description Language (WDL), Cromwell and Docker makes genomic data processing reproducible and (not completely) automatized.
JSON inputs files must be completed by hand generating user-mistake errors.
__automator__ is a tool that automates input files generation for [bcblab-workflows](https://github.com/labbcb/bcblab-workflows), mainly for WES/WGS workflows.
It also submits workflow jobs to Cromwell Server (through [wftool](https://github.com/labbcb/wftool)).

This systems was designed as the way we do large-scale genomic data at BCBLab and may not be generalized.
It makes some assumptions to work fine and only supports WES/WGS workflows.
The list below presents each _automator subcommands_ available:

- File generation helpers
    - `fastq_tsv` Generate batch TSV file containing FASTQ file paths and metadata
    - `intervals_list` Generate genomic intervals in GATK-style .list format
- Workflow preparation and execution
    - `hc_batch` - Submit a batch TSV file to 'bipmed-haplotype-calling' workflow to Cromwell server.
    - `hc` - Submit FASTQ files to 'bipmed-haplotype-calling' workflow to Cromwell server.
    - `joint` - Submit raw gVCF files to 'joint-analysis' workflow.
    - `automate_batch` Run all workflows: 'bipmed-haplotype-calling' workflow; 'joint-analysis'.
    - `automate` Do everything: TSV file; 'bipmed-haplotype-calling' workflow; 'joint-analysis'.
    
