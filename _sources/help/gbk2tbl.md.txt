# gbk2tbl
---
## Overview
This command converts a GenBank file (with a .gbk or .gb extension) into a feature table (.tbl) and generates a corresponding FASTA file (.fsa). These outputs are necessary for downstream processing with tools like table2asn.

You would generally want to use this when you get Genbank flatfiles (.gbk) from external tools like <a href="https://github.com/gbouras13/phold" target="_blank">phold</a>.

---
## Required Input
- **-i, -\\\-input**: Input GenBank file. *(Required)*

## Optional Parameters
- **-m, -\\\-mincontigsize**: Minimum contig size to process (default: 0).
- **-p, -\\\-prefix**: Prefix for output filenames (default: "seq").

## Output
- `<prefix>.fsa`: FASTA file containing the sequence(s).
- `<prefix>.tbl`: Feature table for GenBank submissions.

## Example Usage
```bash
suvtk gbk2tbl -i annotation.gbk -p myprefix