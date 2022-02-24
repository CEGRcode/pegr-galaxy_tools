PEGR-Galaxy Communication Tools
===========================================================

This repository contains the PEGR-Galaxy communication tools.

Below are the installtion steps need to be performed on machine
where Galaxy is installed and on machine where PEGR is installed.
<br />

Installation steps 
===========================================================
### Galaxy configuration:

These steps follow the recommened practice for additng a custom tool to a Galaxy instance.

Detailed Galaxy documentation is available here:
https://galaxyproject.org/admin/tools/add-tool-tutorial/

1. Copy the folder `pegr-galaxy_tools/tools` to `/srv/galaxy/server/tools`.

2. Update Galaxy configuration files to  the existance of the API tools by including them in the `/srv/galaxy/server/config/too_conf.xml.sample`

  ```<section id="PEGR" name="PEGR">```
  
     <tool file="pegr-galaxy_tools/tools/bam_to_scidx_output_stats.xml" />
     
    <tool file="pegr-galaxy_tools/tools/bedtools_intersectbed_output_stats.xml" />
    
    <tool file="pegr-galaxy_tools/tools/bwa_mem_output_stats_single.xml" />
    
    <tool file="pegr-galaxy_tools/tools/chexmix_output_stats.xml" />
    
    <tool file="pegr-galaxy_tools/tools/cwpair2_output_stats.xml" />
    
    <tool file="pegr-galaxy_tools/tools/extract_genomic_dna_output_stats.xml" />
    
    <tool file="pegr-galaxy_tools/tools/extract_genomic_dna_output_stats2.xml" />
    
    <tool file="pegr-galaxy_tools/tools/extract_genomic_dna_output_stats3.xml" />
    
    <tool file="pegr-galaxy_tools/tools/fasta_nucleotide_color_plot_output_stats.xml" />
    
    <tool file="pegr-galaxy_tools/tools/fastqc_output_stats.xml" />
    
    <tool file="pegr-galaxy_tools/tools/fastqc_output_stats2.xml" />
    
    <tool file="pegr-galaxy_tools/tools/genetrack_output_stats.xml" />
    
    <tool file="pegr-galaxy_tools/tools/input_dataset_r1_output_stats.xml" />
    
    <tool file="pegr-galaxy_tools/tools/input_dataset_r2_output_stats.xml" />`
    
    <tool file="pegr-galaxy_tools/tools/mark_duplicates_bam_output_stats.xml" />
    
    <tool file="pegr-galaxy_tools/tools/meme_fimo_output_stats.xml" />
    
    <tool file="pegr-galaxy_tools/tools/meme_meme_output_stats.xml" />
    
    <tool file="pegr-galaxy_tools/tools/pe_histogram_output_stats.xml" />
    
    <tool file="pegr-galaxy_tools/tools/repeatmasker_wrapper_output_stats.xml" />
    
    <tool file="pegr-galaxy_tools/tools/repeatmasker_wrapper_output_stats2.xml" />
    
    <tool file="pegr-galaxy_tools/tools/samtool_filter2_output_stats.xml" />
    
    <tool file="pegr-galaxy_tools/tools/tag_pileup_frequency_output_stats.xml" />
    
    <tool file="pegr-galaxy_tools/tools/galaxy_post_pegr.xml" />```
    
  ```</section>```
 

3. If using only `galaxy_post_pegr` tool which is generalized API tool for PEGR, update `galaxy_post_pegr_config.ini` by giving the `PEGR_URL` and `PEGR_API_KEY`. 

  Please note, each user in PEGR has an email address and associated API key. The user who logs in to Galaxy and runs the Galaxy pipeline needs to have the same email address in Galaxy and PEGR to be authorized.

4. Restart Galaxy

    ```sudo systemctl restart galaxy```
 
 5. Solve dependencies for local Galaxy tools that have been just added through Galaxy web interface. `Admin->Manage Dependencies`

### PEGR configuration:

These steps update the PEGR system to allow new tools to communicate from Galaxy to PEGR.

5. Navigate on the PEGR interface to:

    `Admin->Pipeline-> New Pipeline`

6. If using only galaxy_post_pegr tool in `Admin->Pipeline->New Pipeline->steps` include the pipeline steps in the following format:

`[[toolId_1, desired_name_1], [toolId_2. desired_name_2],....]`

where each toolId is the Id of the tool in Galaxy for which the API tool is reporting (direct upstream of the API tool). The desired_name is the name you like to see in PEGR as the short name for the tool. For example it can be:

`[['toolshed.g2.bx.psu.edu/repos/devteam/bwa/bwa_mem/0.7.17.1', 'Mapping'], ....]`
<br />
<br />
### Notes on using tool specific API tools:
If using tool specific API tools step 3 and step 6 needs to be modified as the following:

A. Step 3 should be replaced with:

  3a. `cp stats_config.ini.sample stats_config.ini`
  
  3b. Update the `default` section  of `stats_config.ini` by giving the `PEGR_URL` and `PEGR_API_KEY`. 

  3c. Define tool_category for each tool where left hand side is the tool for which the galaxy is reporting and right hand side is interpertable by PEGR.

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

B. Step 5 shold be replaced with:

  5a. In PEGR: Admin->pipeline->steps include the pipeline steps in the following format:

  `[[StatstoolId_1, desired_name_1], [StatstoolId_2. desired_name_2],....]`

  where each StatstoolId is the Id of the specific API tool. The desired_name is the name you like to see as the short name for the tool. For example it can be:

  `[['bwa_mem_output_stats_single', 'Mapping'], ....]`

***Please note that using tool specific API tools has the advantage that more information such as different statistics for each specific tool are posted to PEGR, but the downside is that a new API tool needs to be generated for each newly used tool. Using the galaxy_post_pegr tool sends less information to PEGR, but it is compatible with most Galaxy tools and there is no need to generate a new API tool for each newly used Galaxy tool***

Authors
======

Ali Nematbakhsh

William KM Lai

Gretta Kellogg

Greg Von Kuster
