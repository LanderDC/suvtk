# taxonomy

## Overview
This submodule of `suvtk` assigns virus taxonomy to your nucleotide sequences based on the <a href="https://static-content.springer.com/esm/art%3A10.1038%2Fs41587-023-01844-2/MediaObjects/41587_2023_1844_MOESM1_ESM.pdf" target="_blank">ICTV guidelines</a> (ie. classification to the lowest fitting taxon appended with "sp.", eg. “Coronavirus sp.”). It uses an <a href="https://github.com/apcamargo/ictv-mmseqs2-protein-database" target="_blank">MMseqs2 database</a> with all proteins of ICTV ratified viruses downloaded from NCBI. After `mmseqs2` alignment, the taxonomy is then decided with a lowest common ancestor approach (LCA) based on the best hits as implemented with `mmseqs easy-taxonomy`.

After determining the taxonomy, this subcommand also gives you information on any possible segmented viruses in your data. This could be interesting to look more into your data and try to group segments of the same virus together. For this, the [`suvtk co-occurrence`](co-occurrence.md) module can be helpful.

Finally, `suvtk taxonomy` also outputs the mandatory MIUVIG parameters predicted genome structure (segmented, non-segmented, undetermined) and genome type (ssDNA, dsDNA, ssRNA(+), etc.) based on the predicted taxonomy in the `miuvig_taxonomy.tsv` file. This file is a required input of `suvtk comments` but can be generated yourself following subsequent tsv file format:
| contig | pred_genome_type | pred_genome_struc |
|--------|----------|-------|
| <sequence_name_as_in_fasta> | <allowed_value> | <allowed_value> |

```{admonition} Allowed MIUVIG values
:class: note

::::{grid} 
:gutter: 2

:::{grid-item-card} 
genome_pred_struc
^^^ 
segmented | non-segmented | undetermined 
:::

:::{grid-item-card} 
genome_pred_type
^^^ 
DNA | dsDNA | ssDNA | RNA | dsRNA | ssRNA | ssRNA (+) | ssRNA (-) | mixed | uncharacterized 
:::

::::

```

```{admonition} Adding your own taxonomy
:class: tip

You can provide your own taxonomy to the other submodules (eg. `suvtk features`, `suvtk comments`), if it is a tsv file in following format:
| contig | taxonomy | taxid |
|--------|----------|-------:|
| \<sequence_name_as_in_fasta\> | \<lowest fitting taxon\> sp. | \<taxid\> |
|...|...|...|
```

## Required Input
- **-i, -\\\-input**: Input FASTA file with sequences. *(Required)*
- **-o, -\\\-output**: Output directory where results will be saved. *(Required)*
- **-d, -\\\-database**: Path to the suvtk database folder. *(Required)*

## Optional Parameters
- **-s, -\\\-identity**: Minimum sequence identity threshold for hits (default: 0.7).
- **-t, -\\\-threads**: Number of threads to use (default: 4).

## Output
- `taxonomy.tsv`: Main file with taxonomy assignments for each sequence.
- `miuvig_taxonomy.tsv`: MIUVIG-related taxonomy details (ie. predicted genome structure and type).
- `segmented_viruses_info.tsv`: Additional info for segmented viruses (if applicable).

## Example Usage
```bash
suvtk taxonomy -i sequences.fasta -o taxonomy_output -d /path/to/ICTV_db -s 0.7 -t 4
```