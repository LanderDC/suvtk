# features

## Overview
This command creates an <a href="https://www.ncbi.nlm.nih.gov/WebSub/html/help/feature-table.html" target="_blank">NCBI feature table</a> by predicting open reading frames (ORFs) from an input FASTA file with <a href="https://github.com/althonos/pyrodigal" target="_blank">`pyrodigal`</a>. Subsequently, the ORFs get annotated by aligning the protein translations to the <a href="https://bfvd.steineggerlab.workers.dev/" target="_blank">Big Fantastic Virus Database</a> with `mmseqs2` and selecting the protein name of the top hit.

```{dropdown} Example
:open:

:::{code-block} none
>Feature Seq1
73	3537	CDS
			product	RNA-directed RNA polymerase 
			inference	ab initio prediction:pyrodigal-gv:0.3.2
			inference	alignment:MMseqs2:17.b804f:UniProtKB:A5Y5A1,BFVD:A5Y5A1_unrelaxed_rank_001_alphafold2_ptm_model_3_seed_000
>Feature Seq2
92	1645	CDS
			product	Maturation protein
			inference	ab initio prediction:pyrodigal-gv:0.3.2
			inference	alignment:MMseqs2:17.b804f:UniProtKB:A0A8K1XYM6,BFVD:A0A8K1XYM6_unrelaxed_rank_001_alphafold2_ptm_model_3_seed_000
1664	2035	CDS
			product	hypothetical protein
			inference	ab initio prediction:pyrodigal-gv:0.3.2
2037	3962	CDS
			product	RNA-directed RNA polymerase 
			inference	ab initio prediction:pyrodigal-gv:0.3.2
			inference	alignment:MMseqs2:17.b804f:UniProtKB:A0A8S5L3Y1,BFVD:A0A8S5L3Y1_unrelaxed_rank_001_alphafold2_ptm_model_2_seed_000
:::

:::{note}
1. When there is no hit for the predicted ORF, the ORF will be annotated with 'hypothetical protein'.

2. The /inference <a href="https://www.ncbi.nlm.nih.gov/genbank/evidence/" target="_blank">evidence qualifier</a> is further used to add support for the annotation in the feature table:
- ORF prediction: `ab initio prediction:<prediction_software>:<version>`
- ORF annotation: `alignment:<alignment_software>:<version>[:<reference_db1>:<reference_accession1>,<reference_db2>:<reference_accession2>,...]`
:::
```

```{admonition} Reorientation of sequences
:class: tip
Additionally, if a taxonomy file is provided, `suvtk features` will reorient the input nucleotide sequences based on their taxonomy. This means that ssRNA(-) virus sequences (ie. part of the *Negarnaviricota*) will get a negative orientation (3' &rarr; 5') and all other sequences, including unclassified sequences, a positive orientation (5' &rarr; 3'). This reorientation is based on the strand on which the majority of ORFs are found by `pyrodigal`.
```

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

<div style="margin-top: 2em;"></div>

```{admonition} Warning
:class: warning
For now only coding complete sequences (>50% coding capacity) will have predicted features and be present in the feature table (.tbl).
```

## Output
- `proteins.faa`: Protein sequences in FASTA format.
- `miuvig_features.tsv`: MIUVIG-related features details (ie. prediction tool, reference database and search method).
- `reoriented_nucleotide_sequences.fna`: Potentially reoriented nucleotide sequences.
- `alignment.m8`: Alignment file from the protein search.
- One or more feature table files in NCBI format.
- `no_ORF_prediction.txt`: List of sequences with insufficient ORF predictions.

## Example Usage
```bash
suvtk features -i sequences.fasta -o output_dir -d /path/to/database -g 1 --coding-complete --taxonomy taxonomy.tsv -t 4