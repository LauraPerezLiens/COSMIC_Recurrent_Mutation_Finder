COSMIC RECURRENT MUTATION FINDER
==============================

Script
------
cosmic_recurrent_mutation_finder.py

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

Example input files:

| Dataset | Path |
|--------|------|
| Classification TSV | `./Cosmic_Classification_Tsv_v103_GRCh38/Cosmic_Classification_v103_GRCh38.tsv` |
| Sample TSV | `./Cosmic_Sample_Tsv_v103_GRCh38/Cosmic_Sample_v103_GRCh38.tsv` |
| Mutations TSV | `./Cosmic_GenomeScreensMutant_Tsv_v103_GRCh38/Cosmic_GenomeScreensMutant_v103_GRCh38.tsv` |

For convenience you can define:

```bash
CLASS=./Cosmic_Classification_Tsv_v103_GRCh38/Cosmic_Classification_v103_GRCh38.tsv
SAMPLE=./Cosmic_Sample_Tsv_v103_GRCh38/Cosmic_Sample_v103_GRCh38.tsv
MUT=./Cosmic_GenomeScreensMutant_Tsv_v103_GRCh38/Cosmic_GenomeScreensMutant_v103_GRCh38.tsv
```

GENERAL SYNTAX
--------------

Exploration mode:

```bash
python cosmic_recurrent_mutation_finder.py \
  --classification-tsv <classification_tsv> \
  [--where <filter>] \
  --show <column_or_column_pair>
```

Run mode:

```bash
python cosmic_recurrent_mutation_finder.py \
  --classification-tsv <classification_tsv> \
  --sample-tsv <sample_tsv> \
  --mutations-tsv <mutations_tsv> \
  --where <filter> \
  --run \
  --outdir <output_dir>
```

HELP AND DISCOVERY
------------------

1. Show standard help

```bash
python cosmic_recurrent_mutation_finder.py --help
```
<details>
<summary>Full help output</summary>

```
usage: cosmic_recurrent_mutation_finder.py [-h] --classification-tsv CLASSIFICATION_TSV [--where WHERE] [--list-columns] [--show SHOW] [--include-ns]
                                         [--run] [--sample-tsv SAMPLE_TSV] [--mutations-tsv MUTATIONS_TSV] [--outdir OUTDIR]
                                         [--mutation-mode {missense,protein_changing,all}]

Explore Cosmic_Classification TSV files and optionally run the full phenotype/sample/mutation workflow.

Exploration idea:
  1. List the available columns
  2. Show values for one column
  3. Apply filters with --where
  4. Show another column or a two-column combination
  5. Run the final workflow with --run

Filter syntax:
  COL=value     exact match
  COL!=value    exact mismatch
  COL~regex     regex match
  COL!~regex    regex exclusion

Examples:
  --classification-tsv Cosmic_Classification.tsv --list-columns
  --classification-tsv Cosmic_Classification.tsv --show PRIMARY_SITE
  --classification-tsv Cosmic_Classification.tsv --where 'PRIMARY_SITE=skin' --show PRIMARY_HISTOLOGY
  --classification-tsv Cosmic_Classification.tsv --where 'PRIMARY_HISTOLOGY~melanoma' --show PRIMARY_SITE,HISTOLOGY_SUBTYPE_1
  --classification-tsv Cosmic_Classification.tsv --sample-tsv Cosmic_Sample.tsv --mutations-tsv Cosmic_GenomeScreensMutant.tsv --where 'PRIMARY_HISTOLOGY~melanoma' --run --outdir results

options:
  -h, --help            show this help message and exit
  --classification-tsv CLASSIFICATION_TSV
                        Path to Cosmic_Classification TSV or TSV.GZ file.
  --where WHERE         Filter condition. Can be repeated.
  --list-columns        Print column names and exit.
  --show SHOW           Show value counts for one column or combination counts for two columns. Use COL or COL1,COL2.
  --include-ns          Include empty values and 'NS' in exploration output.
  --run                 Run the full phenotype/sample/mutation workflow.
  --sample-tsv SAMPLE_TSV
                        Path to Cosmic_Sample TSV or TSV.GZ file.
  --mutations-tsv MUTATIONS_TSV
                        Path to Cosmic_GenomeScreensMutant TSV or TSV.GZ file.
  --outdir OUTDIR       Output directory for mutation counts.
  --mutation-mode {missense,protein_changing,all}
                        Mutation filtering mode for --run. Default: missense. 'protein_changing' keeps variants with protein-changing consequence terms, 'all' keeps all mutations.

To show dynamic column/value help, run:
  script.py --classification-tsv Cosmic_Classification.tsv --help
```
</details>



2. Show help including detected columns and example values

```bash
python cosmic_recurrent_mutation_finder.py --classification-tsv "$CLASS" --help
```
<details>
<summary>Full help output</summary>

```
usage: cosmic_recurrent_mutation_finder.py [-h] --classification-tsv CLASSIFICATION_TSV [--where WHERE] [--list-columns] [--show SHOW] [--include-ns]
                                         [--run] [--sample-tsv SAMPLE_TSV] [--mutations-tsv MUTATIONS_TSV] [--outdir OUTDIR]
                                         [--mutation-mode {missense,protein_changing,all}]

Explore Cosmic_Classification TSV files and optionally run the full phenotype/sample/mutation workflow.

Exploration idea:
  1. List the available columns
  2. Show values for one column
  3. Apply filters with --where
  4. Show another column or a two-column combination
  5. Run the final workflow with --run

Filter syntax:
  COL=value     exact match
  COL!=value    exact mismatch
  COL~regex     regex match
  COL!~regex    regex exclusion

Examples:
  --classification-tsv Cosmic_Classification.tsv --list-columns
  --classification-tsv Cosmic_Classification.tsv --show PRIMARY_SITE
  --classification-tsv Cosmic_Classification.tsv --where 'PRIMARY_SITE=skin' --show PRIMARY_HISTOLOGY
  --classification-tsv Cosmic_Classification.tsv --where 'PRIMARY_HISTOLOGY~melanoma' --show PRIMARY_SITE,HISTOLOGY_SUBTYPE_1
  --classification-tsv Cosmic_Classification.tsv --sample-tsv Cosmic_Sample.tsv --mutations-tsv Cosmic_GenomeScreensMutant.tsv --where 'PRIMARY_HISTOLOGY~melanoma' --run --outdir results

options:
  -h, --help            show this help message and exit
  --classification-tsv CLASSIFICATION_TSV
                        Path to Cosmic_Classification TSV or TSV.GZ file.
  --where WHERE         Filter condition. Can be repeated.
  --list-columns        Print column names and exit.
  --show SHOW           Show value counts for one column or combination counts for two columns. Use COL or COL1,COL2.
  --include-ns          Include empty values and 'NS' in exploration output.
  --run                 Run the full phenotype/sample/mutation workflow.
  --sample-tsv SAMPLE_TSV
                        Path to Cosmic_Sample TSV or TSV.GZ file.
  --mutations-tsv MUTATIONS_TSV
                        Path to Cosmic_GenomeScreensMutant TSV or TSV.GZ file.
  --outdir OUTDIR       Output directory for mutation counts.
  --mutation-mode {missense,protein_changing,all}
                        Mutation filtering mode for --run. Default: missense. 'protein_changing' keeps variants with protein-changing consequence terms, 'all' keeps all mutations.

Available columns and example filter values:
  - PRIMARY_SITE: 50 unique values; top values: 'soft_tissue' (2029), 'skin' (1241), 'haematopoietic_and_lymphoid_tissue' (616), 'central_nervous_system' (604), 'bone' (451), 'large_intestine' (317), 'lung' (252), 'upper_aerodigestive_tract' (205)
  - SITE_SUBTYPE_1: 308 unique values; top values: 'fibrous_tissue_and_uncertain_origin' (977), 'blood_vessel' (247), 'striated_muscle' (240), 'nerve_sheath' (202), 'colon' (176), 'fat' (157), 'smooth_muscle' (129), 'mouth' (85)
  - SITE_SUBTYPE_2: 276 unique values; top values: 'upper_leg' (67), 'retroperitoneum' (52), 'leg' (47), 'arm' (45), 'foot' (45), 'pelvis' (45), 'abdomen' (44), 'shoulder' (44)
  - SITE_SUBTYPE_3: 'arm' (1), 'breast' (1), 'chest' (1), 'ethmoid' (11), 'face' (1), 'fossa_of_Rosenmuller' (1), 'groin' (1), 'maxillary' (11), 'paranasal' (7), 'piriform_sinus' (2), 'scalp' (1), 'sphenoid' (4)
  - PRIMARY_HISTOLOGY: 215 unique values; top values: 'carcinoma' (1035), 'other' (889), 'glioma' (425), 'lymphoid_neoplasm' (388), 'malignant_melanoma' (334), 'benign_melanocytic_nevus' (295), 'adnexal_tumour' (240), 'haematopoietic_neoplasm' (211)
  - HISTOLOGY_SUBTYPE_1: 911 unique values; top values: 'squamous_cell_carcinoma' (125), 'adenocarcinoma' (120), 'malignant_adnexal_tumour' (119), 'pleomorphic' (112), 'embryonal' (101), 'seborrhoeic_keratosis' (59), 'astrocytoma_Grade_I' (56), 'blue' (55)
  - HISTOLOGY_SUBTYPE_2: 314 unique values; top values: 'anaplastic' (78), 'glioblastoma_multiforme' (40), 'low_grade_dysplasia' (37), 'pilocytic' (33), 'spindle_cell' (32), 'high_grade_dysplasia' (32), 'fibrillary' (30), 'pleomorphic_xanthoastrocytoma' (28)
  - HISTOLOGY_SUBTYPE_3: 39 unique values; top values: 'congenital_neutropenia' (7), 'associated_with_other_haematological_disorder' (4), 't(8;21)' (3), 'chronic_idiopathic_neutropenia' (2), 'sarcoma' (2), 'aggressive_and_associated_with_other_haematological_disorder' (2), 'aplastic_anaemia' (2), 't(15;17)' (1)
  ```
</details>

3. Print column names only

```bash
python cosmic_recurrent_mutation_finder.py \
  --classification-tsv "$CLASS" \
  --list-columns
```
Output: 

```
COSMIC_PHENOTYPE_ID
PRIMARY_SITE
SITE_SUBTYPE_1
SITE_SUBTYPE_2
SITE_SUBTYPE_3
PRIMARY_HISTOLOGY
HISTOLOGY_SUBTYPE_1
HISTOLOGY_SUBTYPE_2
HISTOLOGY_SUBTYPE_3
NCI_CODE
EFO
```

FILTER SYNTAX
-------------

The script supports these filters:

| Filter | Meaning |
|------|--------|
| `COL=value` | exact match |
| `COL!=value` | exact mismatch |
| `COL~regex` | regex match |
| `COL!~regex` | regex exclusion |

Filters can be repeated:

```bash
--where condition1 --where condition2
```

Multiple filters are combined using logical AND.


SHOW ONE COLUMN
---------------

Use --show with one column name to see the values observed in that column
and their counts.

1. Show PRIMARY_SITE values

```bash 
python cosmic_recurrent_mutation_finder.py \
  --classification-tsv "$CLASS" \
  --show PRIMARY_SITE
```
Example output (truncated):
```
# total_rows    7149
# filtered_rows 7149
# show: PRIMARY_SITE
PRIMARY_SITE    count
soft_tissue     2029
skin    1241
haematopoietic_and_lymphoid_tissue      616
central_nervous_system  604
bone    451
large_intestine 317
lung    252
upper_aerodigestive_tract       205
...
```

2. Show PRIMARY_HISTOLOGY values

```bash 
python cosmic_recurrent_mutation_finder.py \
  --classification-tsv "$CLASS" \
  --show PRIMARY_HISTOLOGY
```
Example output (truncated):
```
# total_rows    7149
# filtered_rows 7149
# show: PRIMARY_HISTOLOGY
PRIMARY_HISTOLOGY       count
carcinoma       1035
other   889
glioma  425
lymphoid_neoplasm       388
malignant_melanoma      334
benign_melanocytic_nevus        295
adnexal_tumour  240
haematopoietic_neoplasm 211
...
```

3. Show PRIMARY_HISTOLOGY values only in skin samples

```bash
python cosmic_recurrent_mutation_finder.py \
  --classification-tsv "$CLASS" \
  --where 'PRIMARY_SITE=skin' \
  --show PRIMARY_HISTOLOGY
```
Output:

```# total_rows    7149
# filtered_rows 1241
# show: PRIMARY_HISTOLOGY
PRIMARY_HISTOLOGY       count
malignant_melanoma      314
benign_melanocytic_nevus        288
adnexal_tumour  239
other   181
carcinoma       108
epidermal_nevus 46
in_situ_epithelial_neoplasm     25
Overgrowth_syndrome     24
lentigo 16
```

4. Show PRIMARY_SITE values only for melanoma rows

```bash
python cosmic_recurrent_mutation_finder.py \
  --classification-tsv "$CLASS" \
  --where 'PRIMARY_HISTOLOGY~melanoma' \
  --show PRIMARY_SITE
```
Output: 
```
# total_rows    7149
# filtered_rows 376
# show: PRIMARY_SITE
PRIMARY_SITE    count
skin    314
soft_tissue     42
eye     14
large_intestine 2
meninges        1
central_nervous_system  1
```


SHOW TWO COLUMNS
----------------

Use --show with two comma-separated columns to inspect combinations.

1. Show PRIMARY_SITE and PRIMARY_HISTOLOGY combinations

```bash
python cosmic_recurrent_mutation_finder.py \
  --classification-tsv "$CLASS" \
  --show PRIMARY_SITE,PRIMARY_HISTOLOGY
```
Example output (truncated): 

```
# total_rows    7149
# filtered_rows 7149
# show: PRIMARY_SITE,PRIMARY_HISTOLOGY
PRIMARY_SITE    PRIMARY_HISTOLOGY       count
central_nervous_system  glioma  425
haematopoietic_and_lymphoid_tissue      lymphoid_neoplasm       387
skin    malignant_melanoma      314
skin    benign_melanocytic_nevus        288
skin    adnexal_tumour  239
haematopoietic_and_lymphoid_tissue      haematopoietic_neoplasm 211
soft_tissue     rhabdomyosarcoma        205
lung    carcinoma       183
...
```

2. Show PRIMARY_SITE and HISTOLOGY_SUBTYPE_1 combinations for melanoma rows

```bash
python cosmic_recurrent_mutation_finder.py \
  --classification-tsv "$CLASS" \
  --where 'PRIMARY_HISTOLOGY~melanoma' \
  --show PRIMARY_SITE,HISTOLOGY_SUBTYPE_1
```
Example output (truncated):
```
# total_rows    7149
# filtered_rows 376
# show: PRIMARY_SITE,HISTOLOGY_SUBTYPE_1
PRIMARY_SITE    HISTOLOGY_SUBTYPE_1     count
skin    nodular 43
skin    superficial_spreading   42
skin    spitzoid        27
skin    desmoplastic    27
skin    lentigo_maligna 17
skin    acral_lentiginous       13
skin    in_situ_melanotic_neoplasm      9
skin    epithelioid     8
...
```

3. Show PRIMARY_HISTOLOGY and HISTOLOGY_SUBTYPE_1 combinations in skin

```bash
python cosmic_recurrent_mutation_finder.py \
  --classification-tsv "$CLASS" \
  --where 'PRIMARY_SITE=skin' \
  --show PRIMARY_HISTOLOGY,HISTOLOGY_SUBTYPE_1
```
Example output (truncated):
```
# total_rows    7149
# filtered_rows 1241
# show: PRIMARY_HISTOLOGY,HISTOLOGY_SUBTYPE_1
PRIMARY_HISTOLOGY       HISTOLOGY_SUBTYPE_1     count
adnexal_tumour  malignant_adnexal_tumour        118
other   seborrhoeic_keratosis   59
benign_melanocytic_nevus        blue    54
benign_melanocytic_nevus        Spitz   45
malignant_melanoma      nodular 43
malignant_melanoma      superficial_spreading   42
benign_melanocytic_nevus        compound        33
carcinoma       Merkel_cell_carcinoma   30
...
```


INCLUDE MISSING VALUES
----------------------

By default the script hides empty values and "NS" in exploration output.

To include them:

```bash
python cosmic_recurrent_mutation_finder.py \
  --classification-tsv "$CLASS" \
  --show SITE_SUBTYPE_1 \
  --include-ns
```
Example output (truncated):
```# total_rows    7149
# filtered_rows 7149
# show: SITE_SUBTYPE_1
SITE_SUBTYPE_1  count
NS      1489
fibrous_tissue_and_uncertain_origin     977
blood_vessel    247
striated_muscle 240
nerve_sheath    202
colon   176
fat     157
smooth_muscle   129
...
```


COMBINING MULTIPLE FILTERS
--------------------------

1. Skin melanoma only

```bash
python cosmic_recurrent_mutation_finder.py \
  --classification-tsv "$CLASS" \
  --where 'PRIMARY_SITE=skin' \
  --where 'PRIMARY_HISTOLOGY~melanoma' \
  --show HISTOLOGY_SUBTYPE_1
```
Example output (truncated):
```
# total_rows    7149
# filtered_rows 314
# show: HISTOLOGY_SUBTYPE_1
HISTOLOGY_SUBTYPE_1     count
nodular 43
superficial_spreading   42
spitzoid        27
desmoplastic    27
lentigo_maligna 17
acral_lentiginous       13
in_situ_melanotic_neoplasm      9
epithelioid     8
...
```

2. Exclude benign lesions

```bash
python cosmic_recurrent_mutation_finder.py \
  --classification-tsv "$CLASS" \
  --where 'PRIMARY_SITE=skin' \
  --where 'PRIMARY_HISTOLOGY!=benign_melanocytic_nevus' \
  --show PRIMARY_HISTOLOGY
```
Output:
```
# total_rows    7149
# filtered_rows 953
# show: PRIMARY_HISTOLOGY
PRIMARY_HISTOLOGY       count
malignant_melanoma      314
adnexal_tumour  239
other   181
carcinoma       108
epidermal_nevus 46
in_situ_epithelial_neoplasm     25
Overgrowth_syndrome     24
lentigo 16
```


3. Regex exclusion

```bash
python cosmic_recurrent_mutation_finder.py \
  --classification-tsv "$CLASS" \
  --where 'PRIMARY_SITE=skin' \
  --where 'PRIMARY_HISTOLOGY!~nevus' \
  --show PRIMARY_HISTOLOGY
```
Output:
```
# total_rows    7149
# filtered_rows 907
# show: PRIMARY_HISTOLOGY
PRIMARY_HISTOLOGY       count
malignant_melanoma      314
adnexal_tumour  239
other   181
carcinoma       108
in_situ_epithelial_neoplasm     25
Overgrowth_syndrome     24
lentigo 16
```


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

```bash
python cosmic_recurrent_mutation_finder.py \
  --classification-tsv "$CLASS" \
  --sample-tsv "$SAMPLE" \
  --mutations-tsv "$MUT" \
  --where 'PRIMARY_HISTOLOGY~melanoma' \
  --run \
  --outdir ./results_melanoma
```


RUN OUTPUTS
-----------


The script writes the following file inside `--outdir`.

| File | Description |
|----|----|
| `mutation_counts.tsv` | Recurrent mutation counts across the selected samples |

`mutation_counts.tsv` contains the following columns:

| Column | Description |
|------|-------------|
| `gene` | Gene symbol |
| `mutation` | Protein change or mutation identifier |
| `n_samples` | Number of samples carrying the mutation |


MUTATION MODE
-------------

By default, run mode counts only missense mutations.

Default:

```bash
--mutation-mode missense
```

Available options:

| Mode               | Description                                                                                         |
| ------------------ | --------------------------------------------------------------------------------------------------- |
| `missense`         | Keeps mutations whose `MUTATION_DESCRIPTION` contains `missense_variant`.                           |
| `protein_changing` | Keeps variants that produce a protein change (frameshift, stop gained/lost, in-frame indels, etc.). |
| `all`              | Keeps all mutations found in the selected samples.                                                  |


Detailed definition of protein_changing: 
```
missense_variant
frameshift_variant
stop_gained
stop_lost
start_lost
inframe_insertion
inframe_deletion
protein_altering_variant
```

Examples:

1. Default mode: missense only

```bash
python cosmic_recurrent_mutation_finder.py \
  --classification-tsv "$CLASS" \
  --sample-tsv "$SAMPLE" \
  --mutations-tsv "$MUT" \
  --where 'PRIMARY_HISTOLOGY~melanoma' \
  --run \
  --outdir ./results_melanoma
```


2. Protein-changing mutations

```bash
python cosmic_recurrent_mutation_finder.py \
  --classification-tsv "$CLASS" \
  --sample-tsv "$SAMPLE" \
  --mutations-tsv "$MUT" \
  --where 'PRIMARY_HISTOLOGY~melanoma' \
  --run \
  --mutation-mode protein_changing \
  --outdir ./results_melanoma
```


3. All mutations

```bash
python cosmic_recurrent_mutation_finder.py \
  --classification-tsv "$CLASS" \
  --sample-tsv "$SAMPLE" \
  --mutations-tsv "$MUT" \
  --where 'PRIMARY_HISTOLOGY~melanoma' \
  --run \
  --mutation-mode all \
  --outdir ./results_melanoma
```

NOTES
-----

--help only shows dataset-specific information if --classification-tsv is provided.

Multiple --where filters are combined using AND.

Regex filters are case-insensitive.

NS values are hidden unless --include-ns is used.

Columns such as COSMIC_PHENOTYPE_ID, NCI_CODE, and EFO exist but are not very useful
for manual filtering.
