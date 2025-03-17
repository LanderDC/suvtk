# co-occurrence

## Overview
This command identifies co-occurring sequences in an abundance table based on specified thresholds. It calculates correlation matrices and can output pairwise related contigs or segment-specific correlations.

### Abundance table

### Segment list

### Length file

## Required Input
- **-i, -\\\-input**: Abundance table file (TSV format). *(Required)*
- **-o, -\\\-output**: Prefix for output files. *(Required)*

## Optional Parameters
- **-s, -\\\-segments**: File with a list of contigs of interest (e.g., RdRP segments).
- **-l, -\\\-lengths**: File with the lengths of each contig.
- **-p, -\\\-prevalence**: Minimum percentage of samples for analysis (default: 0.1).
- **-c, -\\\-correlation**: Minimum correlation threshold to consider pairs (default: 0.5).
- **-\\\-strict**: Flag indicating that the correlation threshold must be met for all provided segments.

## Output
- If no segments file is provided:  
  - `<output>_correlation_matrix.tsv` – A masked correlation matrix.
  - `<output>_related_contigs.tsv` – A table of pairwise correlations meeting the threshold.
- If a segments file is provided:  
  - `<output>.tsv` – A correlation matrix filtered based on the segments.

## Example Usage
```bash
suvtk co-occurrence -i abundance.tsv -o results -p 0.1 -c 0.5
