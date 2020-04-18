# Automated and reproducible tool for identifying genomic variants at scale
    
Processing high-throughput sequencing data was the biggest challenge in the past, dealing with small datasets of large sample data.
Genomics projects with thousands of samples have became popular due to decreasing in sequencing costs.
Now we are facing a new challenge: how to process and store large-scale datasets efficiently.

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

Espresso-Caller is a tool that automates execution of workflows for identification of genomic variants from whole-exome and whole-genome datasets.
It collects raw sequencing paired-end FASTQ or raw gVCF files, together with resources files (__b37__ or __hg38__ versions), assessing their existence, to generate the JSON file that is used as input of workflows for processing WES/WGS data.
Our software takes some conventions to automatically find the required files and to define sample metadata.
Internally it submits WDL files to Cromwell server through [Cromwell API](https://cromwell.readthedocs.io/en/stable/api/RESTAPI/).
The next section introduces the workflows, next section provides examples of command lines and explanation of arguments, conventions and outputs.
The last section shows advanced uses of _espresso_
This document ends with the actual usage help.

## Workflows

_espresso_ provides three workflows: __hc__ (HaplotypeCalling) takes raw FASTQ files and their metadata as input plus resources files and generates per-sample raw gVCF alongside unmapped BAM and analysis-ready CRAM files. __joint__ (JointDiscovery) takes raw gVCF files and merge into a single unified VCF; __all__  executes all data processing steps: from raw FASTQs to unified VCF.

Our tool bundles [in-house workflows](https://github.com/labbcb/workflows) and workflows defined by the Broad Institute as [GATK Best Practices](https://software.broadinstitute.org/gatk/) defined in WDL format.
The workflow files are stored inside the tool package.
The list below presents each workflow in the order that is executed by this tool.

[HaplotypeCalling](espresso/workflows/haplotype-calling.wdl) runs the following workflows:

1. [Convert raw paired-end FASTQ files to unmapped BAM format (uBAM)](espresso/workflows/paired-fastq-to-unmapped-bam.wdl)
2. [Map sequences to reference genome, recalibrate alignments and generate analysis-ready BAM files](espresso/workflows/processing-for-variant-discovery-gatk4.wdl)
3. [Produce sample-specific sufficient statistics to call variants](espresso/workflows/haplotypecaller-gvcf-gatk4.wdl)
4. [Validate BAM files](espresso/workflows/validate-bam.wdl)
5. [Convert BAM files to CRAM format](espresso/workflows/bam-to-cram.wdl)

[JointDiscovery](espresso/workflows/joint-discovery-gatk4-local.wdl), we combine the sample-specific sufficient statistics to produce final genotype calls. For this step, we use the original WDL file produced by the Broad Institute.

Espresso-Caller follows some _convention over configuration_ (where configuration is the inputs JSON file).
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
Downloaded files will have the right names to work with _espresso_.

- [b37](download_resources_b37_files.sh)
- [hg38](download_resources_hg38_files.sh)

To download resource files run.
It is important to inform the _absolute path_ to destination directory.

```bash
bash download_resources_b37_files.sh /home/data/ref/b37
bash download_resources_hg38_files.sh /home/data/ref/hg38
```

The following command will run _espresso_ with two directories containing raw FASTQ files.
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
See [installing required software script](install_software.sh).

- `--gatk_path_override` path to __GATK version 4__, it must point to `gatk` wrapper script (not the Jar file).
- `--gotc_path_override` path to directory containing all softwares (`bwa`, `picard.jar`, etc)
- `--samtools_path_override` path to `samtools`.

The `--dont_run` flag does _espresso_ to __not submit workflows to Cromwell server__.
In this mode, the tool will check all required files, copy required workflow files and generate inputs JSON file writing both to destination directory.
It is very recommend that you run our tool in this mode and check JSON file _before_ running in production.
Also, it is useful when there are some change to do in the default JSON file and then submit workflow using _espresso_ instead.

The optional `--move` flag will tell _espresso_ to _move_ output files from Cromwell execution directory to destination directory.
It is useful for processing large-scale genomics datasets avoiding file duplication.

The last two arguments are required: callset name and destination directory to write all files.

```bash
espresso all \
	--fastq ~/raw/batch1 \
	--fastq ~/raw/batch2 \
	--library Batch1 \
	--library Batch2 \
	--date 2018-10-19 \
	--date 2019-02-07 \
	--platform ILLUMINA \
	--platform ILLUMINA \
	--center MyCenter \
	--center MyCenter \
	--reference ~/ref/b37 \
	--version b37 \
	--gatk_path_override ~/bin/gatk-4.1.0.0/gatk \
	--gotc_path_override ~/bin \
	--samtools_path_override ~/bin/samtools-1.9/samtools \
	--move \
	--dont_run \
	MyDataset.b37 \
	~/res/my_dataset
```

	Starting the haplotype-calling workflow with reference genome version b37
	Workflow file: /home/data/res/my_dataset/haplotype-calling.wdl
	Inputs JSON file: /home/data/res/my_dataset/haplotype-calling.b37.inputs.json
	Workflow will not be submitted to Cromwell. See workflow files in /home/data/res/my_dataset

If you run without `--dont_run` argument you will see the text below.
As you can see, after workflow is submitted no output is presented until execution is finished.
Then the tool will print the collected output files and exit.

> In this version __all__ run __hc__ first then __joint__. TODO: write WDL file that do both

	Starting haplotype-calling workflow with reference genome version b37
	Workflow file: /home/data/res/my_dataset/haplotype-calling.wdl
	Inputs JSON file: /home/data/res/my_dataset/haplotype-calling.b37.inputs.json
	Workflow submitted to Cromwell Server (http://localhost:8000)
	Workflow id: 9977f400-d1b6-41ff-ab92-7ebbbf7a30a8

## Expected outputs

At the end of execution _espresso_ will _collect output files_ copying them to destination directory.
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

### Running __hc__ or __joint__ individually

It is possible to run only __hc__ by `espresso hc ...` and __joint__ by `espresso joint ...`.
Running __hc__ is useful when we don't want to generate the unified VCF for theses FASTQ files.
The __joint__ is useful when we already have raw gVCF files and we want to merge to or more data from batches or studies.
However there are some conventions that your VCF files must follow (only if they weren't generated by _espresso_).

- VCF file names must match this pattern: `(sample_name)(.version)?.g.vcf(.gz)?` (it must have `.g.vcf` extension to skip unified VCFs that may exist in the same directory).
- Index files with the same name plus `.tbi` extension in the same directory.


### Reproduce data processing

With WDL and JSON files written in the _result directory_ it is possible to re-execute data processing _without_ espresso.
To do that we need the Cromwell binary file.
It should also works on different workflow engine such as [miniwdl](https://github.com/chanzuckerberg/miniwdl) or workflow submission toolm such as [wf](https://github.com/labbcb/wf).

Run workflow Cromwell in Local mode

```bash
java -jar cromwell.jar run \
	-i /home/data/res/my_dataset/haplotype-calling.b37.inputs.json \
	/home/data/res/my_dataset/haplotype-calling.wdl
```

## Development

# Espresso-Caller development notes

Install latest development version.

```bash
python3 -m venv venv
source venv/bin/activate
pip install -U pip
pip install click requests
pip install git+https://github.com/labbcb/espresso-caller.git
```

Run `espresso` in dry mode.

```bash
FASTQ_DIR=/home/nfs/welliton/code/rnnr-paper/1kgp_50_low_wgs
REF_DIR=/home/nfs/ref/hg38
DATASET_NAME=1KGP_LOW_WGS
RESULT_DIR=espresso-results

espresso all \
    --fastq $FASTQ_DIR \
    --library Phase3 \
    --date 2015-07-30 \
    --platform Illumina \
    --center IGSR \
    --disable_platform_unit \
    --reference $REF_DIR \
    --version hg38 \
    --dont_run \
    $DATASET_NAME \
    $RESULT_DIR
```