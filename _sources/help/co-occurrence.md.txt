# co-occurrence
---
## Overview
This command identifies co-occurring sequences in an abundance table based on specified thresholds. It calculates correlation matrices and can output pairwise related contigs or segment-specific correlations.

### Abundance table
`suvtk co-occurrence` takes an abundance table (contigs should be rows, samples columns) and by default filters out all contigs that are present in less than 10% of the samples. You can get an abundance table by clustering the sequences across all your samples and mapping the reads of each sample back to the cluster representatives.

Example:
```none
         Sample1  Sample2  Sample3  Sample4
Contig1  1839     0        868      0
Contig2  0        729      0        0
Contig3  1303     0        69       0
Contig4  0        0        0        90
```

### Segment list
The `co-occurrence` module also allows you to correlate specific contigs of interest with all other contigs in your study. It needs the names of your contigs of interest (`-s/--segments`). The output is a correlation matrix of all contigs above the correlation threshold with your contigs of interest.

Example:
```
Contig1 
Contig3
etc.
```

### Length file
The abundance table is either transformed to a presence/absence table or, if you provide a file with the contig lengths (`-l/--lengths`), the read count is divided by the contig length. This would take also the abundance of each contig in account without bias towards the length of the contig (larger contigs have more reads, although they might not be that abundant).

Example:
```none
Contig1 7493
Contig2 2923
Contig3 3092
Contig4 1490
```

---
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
```none
suvtk co-occurrence -i abundance.tsv -o results -p 0.1 -c 0.5
