PEGR-Galaxy Communication Tools
===========================================================

This repository contains the PEGR-Galaxy communication tools.

Below are the installtion steps need to be performed on machine
where Galaxy is installed and on machine where PEGR is installed.
<br />

Installation steps 
===========================================================
### Galaxy configuration:

These steps follows basically the recommened practice for additng a custom tool to a Galaxy instance.

Detailed Galaxy documentation is available here:
https://galaxyproject.org/admin/tools/add-tool-tutorial/

1. clone the repository to `local_tools` directory in Galaxy machine.
```
cd /mnt/mountpoint/srv/galaxy/local_tools
sudo git clone https://github.com/CEGRcode/pegr-galaxy_tools
```
2. Update and check the two sections of config file for "tool specific" pegr_api_tools.

```
cd pegr-galaxy_tools/tools
cp stats_config.ini.sample stats_config.ini
```

2.1 In the `[default]` section of `stats_config.ini` file as the following:

```
PEGR_API_KEY = some_api_key**
PEGR_URL = https://hestia.cac.cornell.edu/pegr/api/stats

GALAXY_API_KEY = galaxy_api_key
GALAXY_BASE_URL = https://galaxy.egc.cac.cornell.edu
```

2.2 Check the `[tool_categories]` section of `stats_config.ini` file. The left hand side is the `Galaxy tool ID`* for which the galaxy is reporting to PEGR, and right hand side is the name interpertable by PEGR. If any Galaxy tools in ChIP-exo pieline is updated in future, the left hand side needs to be updated to reflect the new `Galaxy tool ID`. Right now, no update is needed to the default values which are the followings

```

[tool_categories]

input_dataset_r1 = output_fastqRead1

input_dataset_r2 = output_fastqRead2

toolshed.g2.bx.psu.edu/repos/iuc/bam_to_scidx/bam_to_scidx/1.0.1 = output_bamToScidx

toolshed.g2.bx.psu.edu/repos/iuc/bedtools/bedtools_intersectbed/2.27.1+galaxy1 = output_bedtoolsIntersect

toolshed.g2.bx.psu.edu/repos/devteam/bwa/bwa_mem/0.7.17.1 = output_bwaMem

toolshed.g2.bx.psu.edu/repos/iuc/cwpair2/cwpair2/1.1.0 = output_cwpair2

toolshed.g2.bx.psu.edu/repos/iuc/genetrack/genetrack/1.0.1 = output_genetrack

toolshed.g2.bx.psu.edu/repos/iuc/extract_genomic_dna/Extract genomic DNA 1/3.0.3 = output_extractGenomicDNA

toolshed.g2.bx.psu.edu/repos/devteam/fastqc/fastqc/0.72+galaxy1 = output_fastqc

toolshed.g2.bx.psu.edu/repos/iuc/pe_histogram/pe_histogram/1.0.1 = output_peHistogram

toolshed.g2.bx.psu.edu/repos/bgruening/repeat_masker/repeatmasker_wrapper/0.1.2 =output_repeatMasker

toolshed.g2.bx.psu.edu/repos/iuc/meme_meme/meme_meme/4.11.2.0 = output_meme

toolshed.g2.bx.psu.edu/repos/iuc/fasta_nucleotide_color_plot/fasta_nucleotide_color_plot/1.0.1 = output_fourColorPlot

toolshed.g2.bx.psu.edu/repos/jjohnson/samtools_filter/samtools_filter/1.1.1 = output_samtoolFilter

toolshed.g2.bx.psu.edu/repos/devteam/picard/picard_MarkDuplicates/2.7.1.1 = output_markDuplicates

toolshed.g2.bx.psu.edu/repos/iuc/meme_fimo/meme_fimo/4.11.2.0 = output_fimo

toolshed.g2.bx.psu.edu/repos/iuc/tag_pileup_frequency/tag_pileup_frequency/1.0.1 = output_tagPileup

chexmix = output_chexmix

```

3. Update the config file for "general" pegr_api_tools.

```
vi galaxy_post_pegr_config.ini
```
Provide values for the url and api keys for pegr
```
PEGR_API_KEY = some_api_key
PEGR_URL = https://hestia.cac.cornell.edu/pegr/api/stats
```

Please note, each user in PEGR has an email address and associated API key. The same goes for any Galaxy user. The user who logs in to Galaxy and runs the Galaxy pipeline needs to have the same email address in both Galaxy and PEGR to be authorized. Hence, the `PEGR_API_KEY` and `GALAXY_API_KEY` corresponds to "this email" should be given in `galaxy_post_pegr_config.ini` and `stats_config.ini` files.

4. Restart Galaxy

```
sudo systemctl restart galaxy
```
 
5. Solve dependencies for local Galaxy tools that have been just added through Galaxy web interface. `Admin->Manage Dependencies`

## PEGR configuration:

These steps update the PEGR system to allow new tools to communicate from Galaxy to PEGR.

1. Navigate on the PEGR interface to introduce the pipline to PEGR:

    `Admin->Pipeline-> New Pipeline`
    
    <img width="636" alt="Screen Shot 2022-03-23 at 3 53 41 PM" src="https://user-images.githubusercontent.com/14810328/159784417-0a6db4c3-7b2c-4bb6-ad88-caf202a8120c.png">

2. fill out different sections as the following:

**2.1 Workflow Id and Workflow Url**

Open Galaxy web interface->Workflow-> click on the desired workflow -> view

The following url will be shown:
<img width="856" alt="Screen Shot 2022-03-23 at 4 42 11 PM" src="https://user-images.githubusercontent.com/14810328/159791947-52efc3f2-fa3b-4714-8665-81c2cf4e3fbe.png">

In the above snapshot 'f2db41e1fa331b3e' at the end of URL is the `Workflow Id`.
and 'https://galaxy.egc.cac.cornell.edu/workflow/display_by_id?id=f2db41e1fa331b3e' is `Workflow Url`

**2.1 Name and Pipeline Version**

Open Galaxy web interface->Workflow

PEGR assumes the name of the workflow in Galaxy is in the following format:`Name_PipelineVersion`

For example the following `Name` is "pairedPEGR" and `pipeline Version` is: 003
<img width="1102" alt="Screen Shot 2022-03-23 at 4 46 50 PM" src="https://user-images.githubusercontent.com/14810328/159792698-15e6b2b8-f9d4-44b6-9299-2111be9639cf.png">

**2.3 Notes**

Optional. It is just some notes for yourself

**2.4 Steps**

`Steps` depends if you are using only general PEGR api tool, or tool specific API tools. 

If using only "general" PEGR api tool fill out `steps` in the following format:

`[[galaxy_toolID_1, desired_name_1], [galaxy_toolID_2. desired_name_2],....]`

where as an example 'galaxy_toolID_1' represents `galaxy toolID` of the Galaxy tool for which the API tool is reporting (direct upstream of the API tool). The "desired_name" is the name you like to see in PEGR as the short name for the tool. For example it can be:

```
[['toolshed.g2.bx.psu.edu/repos/devteam/bwa/bwa_mem/0.7.17.1', 'Mapping'], ....]
```
<br />
<br />

If using "tool specific" PEGR api tool fill out `steps` in the following format:

`[[galaxy_api_toolID_1, desired_name_1], [galaxy_api_toolID_2. desired_name_2],....]`

where as an example 'galaxy_api_toolID_1' represents `galaxy tool ID` of the tool specific API tool. The "desired_name" is the name you like to see in PEGR as the short name for the tool. For example it can be:

  ```
  [['bwa_mem_output_stats_single', 'Mapping'], ....]

```

Example of `steps` values for ChIP-exo pipeline in "tool specific"  is provided in this repository at `workflows/PEGR_STEPS_Galaxy-Workflow-pairedPEGR_003.txt`

## Foot Notes ##

*`galaxy tool ID` can be found on Galaxy web interface->choose one outputs of the to tool-> click on "i" icon -> Under `Job Informtion`->`Galaxy Tool ID`

** 
PEGR api key can be found as the following

```
ssh some_user@pegr_machine
mysql -u pegr -p
use pegr ;
show tables ;
select api_key,email from user where user='brc_epigenomics@cornell.edu' ;
```



 
*** Please note that using tool specific API tools has the advantage that more information such as different statistics for each specific tool are posted to PEGR, but the downside is that a new API tool needs to be generated for each newly used tool. Using the galaxy_post_pegr tool sends less information to PEGR, but it is compatible with most Galaxy tools and there is no need to generate a new API tool for each newly used Galaxy tool***

Authors
======

Ali Nematbakhsh

William KM Lai

Gretta Kellogg

Greg Von Kuster
