COSMIC CLASSIFICATION EXPLORER
==============================

Script
------
cosmic_classification_explorer.py

Purpose
-------
This script can be used in two ways:

1. Exploration mode:
   - inspect available columns
   - inspect example filter values
   - filter rows using any classification column
   - inspect one column after filtering
   - inspect combinations between two columns after filtering

2. Run mode:
   - apply filters to the COSMIC Classification table
   - retrieve matching COSMIC_PHENOTYPE_ID values internally
   - retrieve the corresponding COSMIC_SAMPLE_ID values internally
   - count recurrent mutations across the selected samples
   - write a final mutation count table

It is useful both for exploring the COSMIC Classification table and for
running the full phenotype/sample/mutation workflow in a single script.


INPUT FILES
-----------

Classification TSV example:

./Cosmic_Classification_Tsv_v103_GRCh38/Cosmic_Classification_v103_GRCh38.tsv

Sample TSV example:

./Cosmic_Sample_Tsv_v103_GRCh38/Cosmic_Sample_v103_GRCh38.tsv

Mutations TSV example:

./Cosmic_GenomeScreensMutant_Tsv_v103_GRCh38/Cosmic_GenomeScreensMutant_v103_GRCh38.tsv

For convenience you can define:

CLASS=./Cosmic_Classification_Tsv_v103_GRCh38/Cosmic_Classification_v103_GRCh38.tsv
SAMPLE=./Cosmic_Sample_Tsv_v103_GRCh38/Cosmic_Sample_v103_GRCh38.tsv
MUT=./Cosmic_GenomeScreensMutant_Tsv_v103_GRCh38/Cosmic_GenomeScreensMutant_v103_GRCh38.tsv


GENERAL SYNTAX
--------------

Exploration mode:

python cosmic_classification_explorer.py \
  --classification-tsv <classification_tsv> \
  [--where <filter>] \
  --show <column_or_column_pair>

Run mode:

python cosmic_classification_explorer.py \
  --classification-tsv <classification_tsv> \
  --sample-tsv <sample_tsv> \
  --mutations-tsv <mutations_tsv> \
  --where <filter> \
  --run \
  --outdir <output_dir>


HELP AND DISCOVERY
------------------

1. Show standard help

python cosmic_classification_explorer.py --help


2. Show help including detected columns and example values

python cosmic_classification_explorer.py --classification-tsv "$CLASS" --help


3. Print column names only

python cosmic_classification_explorer.py \
  --classification-tsv "$CLASS" \
  --list-columns


EXPLORATION LOGIC
-----------------

The intended workflow is:

1. List available columns
2. Show values for one column
3. Apply one or more filters with --where
4. Show another column or a pair of columns inside the filtered subset
5. Once the cohort is well defined, run the full workflow with --run


FILTER SYNTAX
-------------

The script supports these filters:

COL=value     exact match
COL!=value    exact mismatch
COL~regex     regex match
COL!~regex    regex exclusion

Filters can be repeated:

--where condition1 --where condition2

Multiple filters are combined using logical AND.


SHOW ONE COLUMN
---------------

Use --show with one column name to see the values observed in that column
and their counts.

1. Show PRIMARY_SITE values

python cosmic_classification_explorer.py \
  --classification-tsv "$CLASS" \
  --show PRIMARY_SITE


2. Show PRIMARY_HISTOLOGY values

python cosmic_classification_explorer.py \
  --classification-tsv "$CLASS" \
  --show PRIMARY_HISTOLOGY


3. Show PRIMARY_HISTOLOGY values only in skin samples

python cosmic_classification_explorer.py \
  --classification-tsv "$CLASS" \
  --where 'PRIMARY_SITE=skin' \
  --show PRIMARY_HISTOLOGY


4. Show PRIMARY_SITE values only for melanoma rows

python cosmic_classification_explorer.py \
  --classification-tsv "$CLASS" \
  --where 'PRIMARY_HISTOLOGY~melanoma' \
  --show PRIMARY_SITE


SHOW TWO COLUMNS
----------------

Use --show with two comma-separated columns to inspect combinations.

1. Show PRIMARY_SITE and PRIMARY_HISTOLOGY combinations

python cosmic_classification_explorer.py \
  --classification-tsv "$CLASS" \
  --show PRIMARY_SITE,PRIMARY_HISTOLOGY


2. Show PRIMARY_SITE and HISTOLOGY_SUBTYPE_1 combinations for melanoma rows

python cosmic_classification_explorer.py \
  --classification-tsv "$CLASS" \
  --where 'PRIMARY_HISTOLOGY~melanoma' \
  --show PRIMARY_SITE,HISTOLOGY_SUBTYPE_1


3. Show PRIMARY_HISTOLOGY and HISTOLOGY_SUBTYPE_1 combinations in skin

python cosmic_classification_explorer.py \
  --classification-tsv "$CLASS" \
  --where 'PRIMARY_SITE=skin' \
  --show PRIMARY_HISTOLOGY,HISTOLOGY_SUBTYPE_1


INCLUDE MISSING VALUES
----------------------

By default the script hides empty values and "NS" in exploration output.

To include them:

python cosmic_classification_explorer.py \
  --classification-tsv "$CLASS" \
  --show SITE_SUBTYPE_1 \
  --include-ns


COMBINING MULTIPLE FILTERS
--------------------------

1. Skin melanoma only

python cosmic_classification_explorer.py \
  --classification-tsv "$CLASS" \
  --where 'PRIMARY_SITE=skin' \
  --where 'PRIMARY_HISTOLOGY~melanoma' \
  --show HISTOLOGY_SUBTYPE_1


2. Exclude benign lesions

python cosmic_classification_explorer.py \
  --classification-tsv "$CLASS" \
  --where 'PRIMARY_SITE=skin' \
  --where 'PRIMARY_HISTOLOGY!=benign_melanocytic_nevus' \
  --show PRIMARY_HISTOLOGY


3. Regex exclusion

python cosmic_classification_explorer.py \
  --classification-tsv "$CLASS" \
  --where 'PRIMARY_SITE=skin' \
  --where 'PRIMARY_HISTOLOGY!~nevus' \
  --show PRIMARY_HISTOLOGY


RUN MODE
--------

Run mode applies the selected classification filters, retrieves phenotype IDs
internally, retrieves the corresponding sample IDs internally, and counts
recurrent mutations in the selected cohort.

Required arguments for --run:

- --classification-tsv
- --sample-tsv
- --mutations-tsv
- --outdir

Example: run the full workflow for melanoma

python cosmic_classification_explorer.py \
  --classification-tsv "$CLASS" \
  --sample-tsv "$SAMPLE" \
  --mutations-tsv "$MUT" \
  --where 'PRIMARY_HISTOLOGY~melanoma' \
  --run \
  --outdir ./results_melanoma


RUN OUTPUTS
-----------

The script writes this file inside --outdir:

- mutation_counts.tsv

mutation_counts.tsv contains:

gene    mutation    n_samples


MUTATION MODE
-------------

By default, run mode counts only missense mutations.

Default:

--mutation-mode missense

Available options:

- missense
- protein_changing
- all

Mode definitions:

1. missense
   Keeps mutations whose MUTATION_DESCRIPTION contains:
   - missense_variant

2. protein_changing
   Keeps mutations whose MUTATION_DESCRIPTION contains at least one of:
   - missense_variant
   - frameshift_variant
   - stop_gained
   - stop_lost
   - start_lost
   - inframe_insertion
   - inframe_deletion
   - protein_altering_variant

3. all
   Keeps all mutations found in the selected samples.

Examples:

1. Default mode: missense only

python cosmic_classification_explorer.py \
  --classification-tsv "$CLASS" \
  --sample-tsv "$SAMPLE" \
  --mutations-tsv "$MUT" \
  --where 'PRIMARY_HISTOLOGY~melanoma' \
  --run \
  --outdir ./results_melanoma


2. Protein-changing mutations

python cosmic_classification_explorer.py \
  --classification-tsv "$CLASS" \
  --sample-tsv "$SAMPLE" \
  --mutations-tsv "$MUT" \
  --where 'PRIMARY_HISTOLOGY~melanoma' \
  --run \
  --mutation-mode protein_changing \
  --outdir ./results_melanoma


3. All mutations

python cosmic_classification_explorer.py \
  --classification-tsv "$CLASS" \
  --sample-tsv "$SAMPLE" \
  --mutations-tsv "$MUT" \
  --where 'PRIMARY_HISTOLOGY~melanoma' \
  --run \
  --mutation-mode all \
  --outdir ./results_melanoma


SUGGESTED WORKFLOW
------------------

1. List the available columns

python cosmic_classification_explorer.py \
  --classification-tsv "$CLASS" \
  --list-columns


2. Inspect PRIMARY_SITE

python cosmic_classification_explorer.py \
  --classification-tsv "$CLASS" \
  --show PRIMARY_SITE


3. Inspect histologies inside skin

python cosmic_classification_explorer.py \
  --classification-tsv "$CLASS" \
  --where 'PRIMARY_SITE=skin' \
  --show PRIMARY_HISTOLOGY


4. Inspect melanoma-related locations

python cosmic_classification_explorer.py \
  --classification-tsv "$CLASS" \
  --where 'PRIMARY_HISTOLOGY~melanoma' \
  --show PRIMARY_SITE


5. Inspect subtype structure inside the filtered cohort

python cosmic_classification_explorer.py \
  --classification-tsv "$CLASS" \
  --where 'PRIMARY_SITE=skin' \
  --where 'PRIMARY_HISTOLOGY~melanoma' \
  --show HISTOLOGY_SUBTYPE_1,HISTOLOGY_SUBTYPE_2


6. Run the full workflow once the filters are defined

python cosmic_classification_explorer.py \
  --classification-tsv "$CLASS" \
  --sample-tsv "$SAMPLE" \
  --mutations-tsv "$MUT" \
  --where 'PRIMARY_HISTOLOGY~melanoma' \
  --run \
  --outdir ./results_melanoma


NOTES
-----

--help only shows dataset-specific information if --classification-tsv is provided.

Multiple --where filters are combined using AND.

Regex filters are case-insensitive.

NS values are hidden unless --include-ns is used.

Columns such as COSMIC_PHENOTYPE_ID, NCI_CODE, and EFO exist but are not very useful
for manual filtering.

If no exploration option or --run is provided, the script prints a message
explaining that you can either explore the classification table or run the
full workflow.