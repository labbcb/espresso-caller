# Automated and reproducible tool for identifying genomic variations at scale
    
Processing high-throughput sequencing data was the biggest challenge in the past, dealing with small datasets of large sample data. Genomics projects with thousands of samples have became very popular due to decreasing in sequencing costs generating even more data. In the future we will be facing a more difficult challenge: how to process and store large-scale datasets efficiently.

The [Sequence Alignment/Map Format Specification (SAM)](https://samtools.github.io/hts-specs/SAMv1.pdf) and its binary version (BAM) is the most popular and recommended file format to store sequence alignment data. However, due to the increasing throughput of sequencing platforms, BAM files have lost their efficiency, as we are dealing more frequently with deeper whole-genome sequencing (WGS), whole-exome sequencing (WES) and other large-scale genomics data.

The [CRAM file format](https://samtools.github.io/hts-specs/CRAMv3.pdf) is an  improved version of SAM format. Instead of storing DNA sequences aligned to a reference genome, it stores only the _differences_ between the sample and the genome sequence. With this feature, it [reduces dramatically the file sizes](http://www.htslib.org/benchmarks/CRAM.html). To use this new format, common tools, like [Samtools](http://samtools.github.io), require the original genome file (normally in FASTA format).

On another front, different computational tools have been developed to address different problems and they are often chained together in a pipeline to solve a bigger problem. For example, a basic variant caller workflow will:

1. map the reads from a FASTQ file to a reference genome;
2. use the allelic counts at each site to call a genotype.

It is often the case that each of the aforementioned steps will be performed by a different tool (like BWA + GATK). To assist on this matter (combining different tools, linking the output of one step to the input of the following), languages that are agnostic to the choice of platform were developed. These languages allow us to *describe* _tasks_ and combine them into _workflows_, using a dialect closer to the research domain and distant from the computer science domain. [Common Workflow Language (CWL)](https://www.commonwl.org), [Nextflow](https://www.nextflow.io) and [Workflow Description Language (WDL)](http://www.openwdl.org) are the most popular languages to define workflows for processing genomics data. It is important to highlight that these languages only describe what needs to be done.

As an actual user, one expects that the aforementioned tasks/workflows are *executed* to produce results of interest. For this reason, researchers developed _workflow execution systems_, which combine workflow files (`.cwl`, `.nf` or `.wdl`) with parameter files (`.json` of `.yaml`) and input data to generate a _dependency tree_ and actually _execute the processing tasks_.
The most popular workflow executors are: [Toil](https://toil.readthedocs.io/en/latest/) and [Cromwell](http://cromwell.readthedocs.io).
These tools are flexible enough to support different _computing backends_ such as local, cluster, custom environments and cloud.

Distributing bioinformatics tools and keeping track of their versions between several workflows and computing nodes have become a big problem for both system administrators (system updates breaks user tools) and users (updated version o tool outputs _different results_, compromising the reproducibility of the research -- for more information see [FAIR Guiding Principles](https://www.nature.com/articles/sdata201618)).
To solve this problem the research community adopted container technologies, mainly [Singularity](https://sylabs.io/docs/) and [Docker](https://www.docker.com). Projects like [BioContainers](https://biocontainers.pro) provide thousands of container images of bioinformatics tools.
Also, [Docker Hub](https://hub.docker.com) is the main repository for popular open-source projects.

Back to workflows... the workflow file + inputs file have been working well for small datasets. With our [wftools](https://github.com/labbcb/wftools) software, we can submit workflows (and their inputs) to execution services, such as Cromwell in server mode, check workflow executions status and logs, and collect output files copying them to desirable directory. The input JSON file must contain workflow-specific parameter to work, for example, a workflow that require FASTQ files as input we have to provide a _list of absolute paths to FASTQ files_ (two list if paired-end), other workflows may require several resource files that can be specific for different genome versions. It is important to note that Cromwell checks the file existence immediately prior to its use within the task, and this is associated with several downstream errors that force the system to abort the execution of the workflow. Additionally, the input JSON files are manually produced.

This document presents _espresso_ (working title), a tool that _automates execution of workflows for processing whole-exome and whole-genome datasets_.
It collects raw sequencing paired-end FASTQ or raw gVCF files, together with resources files (__b37__ or __hg38__ versions), assessing their existence, to generate the JSON file that is used as input of workflows for processing WES/WGS data.
Our software takes some conventions to automatically find the required files and to define sample metadata.
Internally it submits WDL files to Cromwell server through [Cromwell API](https://cromwell.readthedocs.io/en/stable/api/RESTAPI/).
The next section introduces the workflows, next section provides examples of command lines and explanation of arguments, conventions and outputs.
The last section shows advanced uses of _wftools_
This document ends with the actual usage help.

## Workflows

_espresso_ provides three workflows: __hc__ (haplotype-calling) takes raw FASTQ files and their metadata as input plus resources files and generates per-sample raw gVCF alongside unmapped BAM and analysis-ready CRAM files. __joint__ (joint-discovery) takes raw gVCF files and merge into a single unified VCF; __all__ (variant-discovery - working title) executes all data processing steps: from raw FASTQs to unified VCF.

Our tool wraps several [in-house workflows](https://github.com/labbcb/workflows) and workflows defined by the Broad Institute as [GATK Best Practices](https://software.broadinstitute.org/gatk/) defined in WDL format.
The workflow files are stored inside the tool package.
The list below presents each workflow in the order that is executed by this tool.

[__haplotype-calling__](https://github.com/labbcb/bcblab-workflows/blob/master/haplotype-calling/2.0.0/haplotype-calling.wdl) runs the following workflows in this order:

1. [Convert raw paired-end FASTQ files to unmapped BAM format (uBAM)](https://github.com/gatk-workflows/seq-format-conversion/blob/master/paired-fastq-to-unmapped-bam.wdl)
2. [Map sequences to reference genome, recalibrate alignments and generate analysis-ready BAM files](https://github.com/gatk-workflows/gatk4-data-processing/blob/master/processing-for-variant-discovery-gatk4.wdl)
3. [Produce sample-specific sufficient statistics to call variants](https://github.com/gatk-workflows/gatk4-germline-snps-indels/blob/master/haplotypecaller-gvcf-gatk4.wdl)
4. [Validate BAM files](https://github.com/gatk-workflows/seq-format-validation/blob/master/validate-bam.wdl)
5. [Convert BAM files to CRAM format](https://github.com/labbcb/workflows/blob/master/workflows/bam-to-cram/1.0.0/bam-to-cram.wdl)

[__joint-discovery__](https://github.com/gatk-workflows/gatk4-germline-snps-indels/blob/master/joint-discovery-gatk4.wdl), we combine the sample-specific sufficient statistics to produce final genotype calls. For this step, we use the original WDL file produced by the Broad Institute.

> TODO create a WDL file for this one.

## Running espresso-caller

_espresso_ requires Python 3.4 or higher.
It is a private project hosted at [BCBLab GitHub repository](https://github.com/labbcb/espresso).
TO install run this commands:

```bash
pip3 install --user --force git+https://github.com/labbcb/wftools.git
pip3 install --user --force git+https://github.com/labbcb/espresso.git
```

Our software use some _convention over configuration_ (where configuration is the inputs JSON file).
Your data files must files the following conventions to work:

For __all__ and __hc__:

- Partial FASTQ files were previously merged into a single one
- Each sample is paired-end sequencing data divided in two FASTQ files by strand: forward and reverse  
- FASTQ files are located at the same directory, one directory for each library name/batch
- FASTQ file names matches this pattern: `(sample_name)_R?[12].fastq(.gz)?`
- FASTQ sequence headers match this pattern: `@_:_:(sample_id):(flowcell):_:_:_:_:_:(primer)` which is merged as `sample_id.flowcell.primer`
- Resource files, including reference genome files, are in the same directory, one directory for each version
- Resource files have the same name from download URL
- Destination directory does not exist or is empty, any conflicting file __will be overwritten__ silently
- Relative paths are allowed in command arguments

Resource files can be downloaded using the following scripts.
Downloaded files will have the right names to work with _wftools_.

- [b37](https://github.com/labbcb/bcblab-workflows/blob/master/download_resources_b37_files.sh)
- [hg38](https://github.com/labbcb/bcblab-workflows/blob/master/download_resources_hg38_files.sh)

To download resource files run.
It is important to inform the _absolute path_ to destination directory.

```bash
bash download_resources_b37_files.sh /home/benilton/bioinf/ref/b37
bash download_resources_hg38_files.sh /home/benilton/bioinf/ref/hg38
```

The following command will run _wftools_ with two directories containing raw FASTQ files.
Samples files can be separated by directories to use different metadata for each group of samples (or batch).
If two `--fastq <fastq directory>` argument is defined you have to inform the following arguments twice.

- `--library <library name>` Library (`LB` SAM tag)
- `--date` Sequencing run date(`DT` SAM tag) - _Must be ISO8601 format (YYYY-MM-DD)!_
- `--platform` Sequencing platform (`PL` SAM tag)
- `--center` Sequencing center (`CN` SAM tag)

Also, sample name (`SM`), platform unit (`PU`) are extracted from FASTQ automatically by using predefined conventions.

Next we have to inform the path to resources files (`--reference <resources directory>`) and the reference genome version (only __b37__ and __hg38__ are supported), `--version <genome version>`.

Some computing environments do not support container technology.
In this case we have to inform the _absolute paths_ to this software.
See [installing required software script](https://github.com/labbcb/bcblab-workflows/blob/master/install_softwares.sh).

- `--gatk_path_override` path to __GATK version 4__, it must point to `gatk` wrapper script (not the Jar file).
- `--gotc_path_override` path to directory containing all softwares (`bwa`, `picard.jar`, etc)
- `--samtools_path_override` path to `samtools`.

The `--dont_run` flag does _wftools_ to __not submit workflows to Cromwell server__.
In this mode, the tool will check all required files, copy required workflow files and generate inputs JSON file writing both to destination directory.
It is very recommend that you run our tool in this mode and check JSON file _before_ running in production.
Also, it is useful when there are some change to do in the default JSON file and then submit workflow using _wftools_ instead.

The optional `--move` flag will tell _wftools_ to _move_ output files from Cromwell execution directory to destination directory.
It is useful for processing large-scale genomics datasets avoiding file duplication.

The last two arguments are required: callset name and destination directory to write all files.

```bash
espresso all \
 --fastq ~/bioinf/raw/projdc/batch1 \
 --fastq ~/bioinf/raw/projdc/batch2 \
 --library batch1 \
 --library batch2 \
 --date 2018-10-19 \
 --date 2019-02-07 \
 --platform ILLUMINA \
 --platform ILLUMINA \
 --center Macrogen \
 --center Macrogen \
 --reference ~/bioinf/ref/b37 \
 --version b37 \
 --gatk_path_override ~/bioinf/bin/gatk-4.1.0.0/gatk \
 --gotc_path_override ~/bioinf/bin \
 --samtools_path_override ~/bioinf/bin/samtools-1.9/samtools \
 --move \
 --dont_run \
 projdc.b37 \
 ~/bioinf/res/projdc_b37
```

	Starting the haplotype-calling workflow with reference genome version b37
	Workflow file: /home/benilton/bioinf/res/projdc_b37/haplotype-calling.wdl
	Inputs JSON file: /home/benilton/bioinf/res/projdc_b37/haplotype-calling.b37.inputs.json
	Workflow will not be submitted to Cromwell. See workflow files in /home/benilton/bioinf/res/projdc_b37

If you run without `--dont_run` argument you will see the text below.
As you can see, after workflow is submitted no output is presented until execution is finished.
Then the tool will print the collected output files and exit.

> In this version __all__ run __hc__ first then __joint__. TODO: write WDL file that do both

	Starting haplotype-calling workflow with reference genome version b37
	Workflow file: /home/benilton/bioinf/res/projdc_b37/haplotype-calling.wdl
	Inputs JSON file: /home/benilton/bioinf/res/projdc_b37/haplotype-calling.b37.inputs.json
	Workflow submitted to Cromwell Server (http://localhost:8000)
	Workflow id: 9977f400-d1b6-41ff-ab92-7ebbbf7a30a8

## Expected outputs

At the end of execution _wftools_ will _collect output files_ copying them to destination directory.
These are the file you expect to see.

- `{callset}.vcf.gz` is the _final unified VCF file_  where `callset` was previously defined (index `{callset}.vcf.gz.tbi`)
- `haplotype-calling.wdl` is __hc__ workflow in WDL
- `joint-discovery-gatk4-local.wdl` is __joint__ workflow in WDL
- `haplotype-calling.{version}.inputs.json` is inputs for __hc__ where `version` is __b37__ or __hg38__
- `joint-discovery.{version}.inputs.json` is inputs for __joint__
- `out.intervals` is an intervals files used by __joint__ to call variants on all samples
- `{callset}.variant_calling_detail_metrics` is the variant call metrics files
- `{callset}.variant_calling_summary_metrics` summary variant calling metrics file

For each sample it should have.

- `{sample}.{version}.g.vcf.gz` is raw gVCF file where `sample` was extracted from FASTQ file name (index `{sample}.{version}.g.vcf.gz.tbi`)
- `{sample}.{version}.cram` is the analysis-ready CRAM file (contains both aligned sequences and sequences that weren't mapped at the end of file)
- `{sample}.{version}.duplicate_metrics` is the duplication metrics file
- `{sample}.{version}.validation_.txt` is the BAM validation output file
- `{sample}.unmapped.bam` is the unmapped sequences in BAM format (exactly the same sequences from FASTQ but with recalibrated qualities)
- `{sample}.{version}.recal_data.csv` is the file used to recalibrate PHRED qualities


## Advanced guide

### Time-based processing workflow

At BCBLab we receive _batches_ of sequencing data yearly.
It is very recommend to merge _all per-sample raw gVCF files_, the old ones with new data to improve GATK variant calling accuracy.
_wftools_ collects, through `--vcf <raw gVCFs directory>` argument, previously generated VCF files in the 'joint-discovery' workflow.
Here an example of how it works.
Each result directory will have an unified VCF files containing all sample from previous years.

```bash
# processing 2019 datasets
espresso all \
	--fastq /data/raw/bipmed/batch_2019 \
	--library batch_2019 --date 2019 --platform ILLUMINA --center Macrogen \
	--genome /home/benilton/bioinf/ref/hg38 --version hg38 \
	BIPMed.2019.hg38 \
	/data/res/bipmed/batch_2019/hg38

# processing 2020 datasets
espresso all \
	--fastq /data/raw/bipmed/batch_2020 \
	--vcf /data/res/bipmed/batch_2019/hg38 \
	--library batch_2020 --date 2020 --platform ILLUMINA --center Macrogen \
	--genome /home/benilton/bioinf/ref/hg38 --version hg38 \
	BIPMed.2020.hg38 \
	/data/res/bipmed/batch_2020/hg38

# processing 2021 datasets
espresso all \
	--fastq /data/raw/bipmed/batch_2021 \
	--vcf /data/res/bipmed/batch_2019/hg38 \
	--vcf /data/res/bipmed/batch_2020/hg38 \
	--library batch_2021 --date 2021 --platform ILLUMINA --center Macrogen \
	--genome /home/benilton/bioinf/ref/hg38 --version hg38 \
	BIPMed.2021.hg38 \
	/data/res/bipmed/2021/hg38
```

### Running __hc__ or __joint__ individually

It is possible to run only __hc__ by `espresso hc ...` and __joint__ by `espresso joint ...`.
Running __hc__ is useful when we don't want to generate the unified VCF for theses FASTQ files.
The __joint__ is useful when we already have raw gVCF files and we want to merge to or more data from batches or studies.
However there are some conventions that your VCF files must follow (only if they weren't generated by _espresso_).

- VCF file names must match this pattern: `(sample_name)(.version)?.g.vcf(.gz)?` (it must have `.g.vcf` extension to skip unified VCFs that may exist in the same directory).
- Index files with the same name plus `.tbi` extension in the same directory.


### Submit previously generated inputs file using _wftools_

Validate workflow file

```bash
wftools validate /home/benilton/bioinf/res/projdc_b37/haplotype-calling.wdl
```

	Valid

Submit workflow to Cromwell server

```bash
wftools submit \
	--inputs /home/benilton/bioinf/res/projdc_b37/haplotype-calling.b37.inputs.json \
	/home/benilton/bioinf/res/projdc_b37/haplotype-calling.wdl
```

Check status

```bash
wftools status
```

Collect output files _moving_ them to directory.
When `--move` is used the output files are moved from Cromwell _root execution directory_ to the specified one.
The `--no-task-dir` flag is used to no create sub-directories for each task.
As we know that haplotype-calling and joint-discovery do not output files with the same name we can skip this.

```bash
wftools collect --no-task-dir --move <workflow id>  ~/bioinf/res/projdc_b37
```

---

	Usage: espresso [OPTIONS] COMMAND [ARGS]...

	  Automates execution of workflows for processing WES/WGS data

	  Raw paired-end FASTQ or raw gVCF files are collected, together with
	  resources files (b37 or hg38) to generate JSON file that is used as input
	  for data processing workflows (haplotype-calling, joint-discovery or
	  both). It assumes that each directory containing FASTQ files is a library
	  or batch. FASTQ file names must follow this pattern:
	  (sample_name)_R?[12].fastq(.gz)? Input and resources files are checked
	  before workflows are submitted to Cromwell server. Output files are
	  collected writing them to destination directory.

	  'variant-discovery' workflow executes all data processing steps: from raw
	  FASTQs to unified VCF. It is also able to combine previous raw gVCF files
	  when executing 'joint-discovery' workflow.

	  'haplotype-calling' workflow takes FASTQ files and their metadata as input
	  (plus resources files) and run Broad Institute GATK workflows: convert
	  FASTQ to uBAM; align sequences to reference genome; merge aligned with
	  unmapped sequences to create ready-analysis BAM; validate BAM files;
	  convert BAM files to CRAM format; and call variants generating one raw
	  gVCF per sample.

	  'joint-discovery' workflows takes raw gVCF files and merge into a single
	  unified VCF.

	Options:
	  --help  Show this message and exit.

	Commands:
	  all    Run haplotype-calling and joint-discovery workflows
	  hc     Run only haplotype-calling workflow
	  joint  Run only joint-discovery-gatk4 workflow
