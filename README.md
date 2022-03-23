PEGR-Galaxy Communication Tools
===========================================================

This repository contains the PEGR-Galaxy communication tools.

Below are the installtion steps need to be performed on machine
where Galaxy is installed and on machine where PEGR is installed.
<br />

Installation steps 
===========================================================
## Galaxy configuration:

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

## PEGR configuration:

These steps update the PEGR system to allow new tools to communicate from Galaxy to PEGR.

5. Navigate on the PEGR interface to introduce the pipline to PEGR:

    `Admin->Pipeline-> New Pipeline`
    
    <img width="636" alt="Screen Shot 2022-03-23 at 3 53 41 PM" src="https://user-images.githubusercontent.com/14810328/159784417-0a6db4c3-7b2c-4bb6-ad88-caf202a8120c.png">

Infomraiton to fill out different sections can be found at Galaxy web interface as the following:

**Workflow Id** and **Workflow Url**

Workflow-> click on the desired workflow -> view

The following url will be shown:
<img width="856" alt="Screen Shot 2022-03-23 at 4 42 11 PM" src="https://user-images.githubusercontent.com/14810328/159791947-52efc3f2-fa3b-4714-8665-81c2cf4e3fbe.png">

'f2db41e1fa331b3e' at the end of URL is the "Workflow Id".

**Name** and **Pipeline Version**

PEGR assumes the name of the workflow in Galaxy is in the following format:`Name_PipelineVersion`

For example the following workflow Name is "pairedPEGR" and pipeline Version is: 003
<img width="1102" alt="Screen Shot 2022-03-23 at 4 46 50 PM" src="https://user-images.githubusercontent.com/14810328/159792698-15e6b2b8-f9d4-44b6-9299-2111be9639cf.png">

**Notes**

Optional. It is just some notes for yourself

**Steps**

If using only `galaxy_post_pegr` tool which is generalized API tool for PEGR, include the pipeline steps in the following format:

`[[Galaxy_Tool_ID_1, desired_name_1], [Galaxy_Tool_ID_2. desired_name_2],....]`

For example `Galaxy_Tool_ID_1` is `Galaxy_Tool_ID` of the tool in Galaxy for which the general PEGR API tool is reporting (direct upstream of the API tool). The desired_name is the name you like to see in PEGR as the short name for the tool. For example it can be:

`[['toolshed.g2.bx.psu.edu/repos/devteam/bwa/bwa_mem/0.7.17.1', 'Mapping'], ....]`
<br />
<br />

If using tool specific API tools steps needs to be in the following format:

 `[[Galaxy_API_Tool_ID_1, desired_name_1], [Galaxy_API_Tool_ID_2. desired_name_2],....]`

  For example `Galaxy_API_Tool_ID_1` is `Galaxy_Tool_ID` of the specific API tool in Galaxy which is reporting. The desired_name is the name you like to see in PEGR as the short name for the tool. For example it can be:

  `[['bwa_mem_output_stats_single', 'Mapping'], ....]`

***Please note that using tool specific API tools has the advantage that more information such as different statistics for each specific tool are posted to PEGR, but the downside is that a new API tool needs to be generated for each newly used tool. Using the galaxy_post_pegr tool sends less information to PEGR, but it is compatible with most Galaxy tools and there is no need to generate a new API tool for each newly used Galaxy tool***

Authors
======

Ali Nematbakhsh

William KM Lai

Gretta Kellogg

Greg Von Kuster
