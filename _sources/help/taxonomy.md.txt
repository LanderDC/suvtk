# taxonomy

## Overview
Assigns virus taxonomy to sequences by comparing input sequences against an ICTV MMseqs database. The command outputs taxonomy assignments and additional details such as segmented virus information.

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