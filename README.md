PEGR-Galaxy Communication Tools
===========================================================

This repository contains the PEGR-Galaxy communication tools.
Tools are copied from https://github.com/seqcode/cegr-galaxy with addition of one generalized pegr API tool.
Downloaded tools can be introduced to Galaxy by the following the below steps. The steps for "Galaxy" are very similar to adding any costum tool to Galaxy.

**Galaxy steps:** 

1- Copy the folder "per-galaxy_tools/tools" to /srv/galaxy/server/tools avaiable in the machine where Galaxy is installed

2- Tell Galaxy about the existance of the API tools by including them in the /srv/galaxy/server/config/too_conf.xml.sample. 

3- If using only galaxy_post_pegr tool which is generalized API tool for PEGR, update galaxy_post_pegr_config.ini by giving the PEGR URL and PEGR_API_KEY. Please note, each user in PEGR has an API key.

4-Restart Galaxy


**PEGR steps:**

5- If using only galaxy_post_pegr tool in PEGR: Admin->pipeline->steps introduce to PEGR this communication:
[[toolId_1, desired_name_1], [toolId_2. desired_name_2],....] 
Where each toolId is the Id of the tool in Galaxy for which the API tool is reporting (direct upstream of the API tool). The desired_name is the name you like to see in PEGR as the short name for the tool. For example it can be:

[['toolshed.g2.bx.psu.edu/repos/devteam/bwa/bwa_mem/0.7.17.1', 'Mapping'], ....]


***If using tool specific API tools, step 3 needs to be updated as the following:***

3a- update galaxy_post_pegr_config.ini default section by giving the PEGR URL and PEGR_API_KEY. 

Please note, each user in PEGR has an API key. The user who runs the galaxy pipeline needs to have the same email and associated api key to be authorized by PEGR to accept receiving the payload.

3b- Define tool_category for each tool where the 

"
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
"

where left hand side is the tool for which the galaxy is reporting and right hand side is interpertable by PEGR.

***If using tool specific tools step 5 also needs to be changed as the following:***

5- in PEGR: Admin->pipeline->steps introduce to PEGR this communication:

[[StatstoolId_1, desired_name_1], [StatstoolId_2. desired_name_2],....] 

Where each StatstoolId is the Id of the specific API tool. The desired_name is the name you like to see as the short name for the tool. For example it can be:

[['bwa_mem_output_stats_single', 'Mapping'], ....]



***Please note that using tool specific API tools has the advantage that more information such as different statistics for each specific tool is posted to PEGR, but the downside is that a new API tool needs to be generated for each newly used tool. Using the galaxy_post_pegr tools sends less information to PEGR, but it is compatible with most Galaxy tools and there is no need to generate new API tools for each newly used Galaxy tool***


