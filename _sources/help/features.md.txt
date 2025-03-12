# features

## Overview
This command creates feature tables for sequences by predicting open reading frames (ORFs) from an input FASTA file. It also generates protein translations and, if necessary, reorients sequences based on taxonomy.

## Required Input
- **-i, -\\\-input**: Input FASTA file with sequences. *(Required)*
- **-o, -\\\-output**: Output directory where the results will be saved. *(Required)*
- **-d, -\\\-database**: Path to the suvtk database folder. *(Required)*

## Optional Parameters
- **-g, -\\\-translation-table**: Translation table (default: 1). Valid codes: 1–6, 9–16, 21–31.
- **-\\\-coding-complete**: Flag to keep only genomes with >50% coding capacity.
- **-\\\-taxonomy**: Taxonomy file for adjusting sequence orientation (particularly for ssRNA(-) viruses).
- **-\\\-separate-files**: Flag to save feature tables into separate files rather than one combined file.
- **-t, -\\\-threads**: Number of threads to use (default: 4).

## Output
- `proteins.faa`: Protein sequences in FASTA format.
- `miuvig_features.tsv`: MIUVIG-related features details (ie. prediction tool, reference database and search method).
- `reoriented_nucleotide_sequences.fna`: Potentially reoriented nucleotide sequences.
- `alignment.m8`: Alignment file from the protein search.
- One or more feature table files in NCBI format.
- `no_ORF_prediction.txt`: List of sequences with insufficient ORF predictions.

## Example Usage
```bash
suvtk features -i sequences.fasta -o output_dir -d /path/to/database -g 1 -\\\-coding-complete -\\\-taxonomy taxonomy.tsv -\\\-separate-files -t 4