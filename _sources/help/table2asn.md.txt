# table2asn

## Overview
Generates a submission file (.sqn) for GenBank by integrating sequence data, feature tables, and structured comment files. It leverages the table2asn utility and validates the submission file.

### Fasta file
Your input sequences, preferably the `reoriented_nucleotide_sequences.fna` from the [`features`](features.md) subcommand.

### Source file
This file contains the metadata of your sequences as required by <a href="https://www.ncbi.nlm.nih.gov/WebSub/html/help/genbank-source-table.html" target="_blank">NCBI</a>. You will have to generate this file yourself from the output of the [`suvtk taxonomy`](taxonomy.md) subcommand and the metadata of your study. The `taxonomy.tsv`file contains the *Sequence_ID* and the *Organism* values, you will have to provide:
- *Isolate* (required; unique identifiers for each sequence, preferably as a single string of at least six alphanumerical characters (e.g., blue53F), using hyphens and underscores to tie separate elements together, e.g., “0815_Eier-kuchen”) 
- *Collection_date* (required; in format [DD-Mon-]YYYY)
- *geo_loc_name* (required; Country of origin)
- *Lat_Lon* (required; coordinates in decimal degrees format: XX.XXX N/S XX.XXX E/W)
- *Bioproject* (Bioproject accession)
- *Biosample* (Biosample accession)
- *SRA* (SRA accession)
- *Segment* (Indicates to which segment this contig belongs, the [`co-occurrence`](co-occurrence.md) module can help with determining more segments of a virus. Leave blank for non-segmented viruses)
- *Metagenomic* (should always be *TRUE*)
- *Metagenome_source* (origin of sample, eg. human gut metagenome, soil metagenome, etc.)

The order of the columns does not matter. <br>
```{dropdown} Example
:open:
| Sequence_ID                              | Organism              | Isolate          | Collection_date | geo_loc_name | Metagenome_source    | Lat_Lon             | Biosample    | SRA         | Segment | Metagenomic |
|------------------------------------------|-----------------------|------------------|-----------------:|--------------|----------------------|---------------------|--------------|-------------|---------:|-------------|
| Seq1 | Riboviria&nbsp;sp.         | Sample1_bazTh | Jul-21          | Cameroon     | blackfly metagenome  | 4.352433&nbsp;N&nbsp;11.63255&nbsp;E | SAMN40472416 | SRR28387210 |         | TRUE        |
| Seq2 | Leviviricetes&nbsp;sp.     | Sample2_8xzwR | Jul-21          | Cameroon     | blackfly metagenome  | 4.352433&nbsp;N&nbsp;11.63255&nbsp;E | SAMN40472429 | SRR28387198 |         | TRUE        |
| Seq3 | unclassified&nbsp;viruses  | Sample3_xliVj | Jul-21          | Cameroon     | blackfly metagenome  | 4.352433&nbsp;N&nbsp;11.63255&nbsp;E | SAMN40472417 | SRR28387209 |         | TRUE        |
| Seq4 | Chrysoviridae&nbsp;sp.     | Sample4_qC6AD | Jul-21          | Cameroon     | blackfly metagenome  | 4.352433&nbsp;N&nbsp;11.63255&nbsp;E | SAMN40472428 | SRR28387197 |    1    | TRUE        |
| Seq5 | Chrysoviridae&nbsp;sp.     | Sample4_qC6AD | Jul-21          | Cameroon     | blackfly metagenome  | 4.352433&nbsp;N&nbsp;11.63255&nbsp;E | SAMN40472428 | SRR28387197 |    2    | TRUE        |
| Seq6 | Chrysoviridae&nbsp;sp.     | Sample4_qC6AD | Jul-21          | Cameroon     | blackfly metagenome  | 4.352433&nbsp;N&nbsp;11.63255&nbsp;E | SAMN40472428 | SRR28387197 |    3    | TRUE        |
| Seq7 | Chrysoviridae&nbsp;sp.     | Sample4_qC6AD | Jul-21          | Cameroon     | blackfly metagenome  | 4.352433&nbsp;N&nbsp;11.63255&nbsp;E | SAMN40472428 | SRR28387197 |    4    | TRUE        |
| Seq8 | Negarnaviricota&nbsp;sp.   | Sample1_IowNh | Jul-21          | Cameroon     | blackfly metagenome  | 4.352433&nbsp;N&nbsp;11.63255&nbsp;E | SAMN40472416 | SRR28387210 |         | TRUE        |
| Seq9 | Riboviria&nbsp;sp.         | Sample3_o7K62 | Jul-21          | Cameroon     | blackfly metagenome  | 4.352433&nbsp;N&nbsp;11.63255&nbsp;E | SAMN40472417 | SRR28387209 |         | TRUE        |
:::{note}
Note that for the segmented virus, the **Isolate** value is the same for all segments.
:::
```

### Template file
You can generate a template file <a href="https://submit.ncbi.nlm.nih.gov/genbank/template/submission/" target="_blank">here</a> to include sequence author information in the Genbank submission.

### Comments file
This file contains structured comments that provide additional metadata for your submission. It should be generated from the [`comments`](comments.md) subcommand.

## Required Input
- **-i, -\\\-input**: Input FASTA file. *(Required)*
- **-o, -\\\-output**: Output prefix (the resulting file will have a `.sqn` extension). *(Required)*
- **-s, -\\\-src-file**: File containing source modifiers (.src). *(Required)*
- **-f, -\\\-features**: Feature table file (.tbl). *(Required)*
- **-t, -\\\-template**: Template file with author information (.sbt). *(Required)*
- **-c, -\\\-comments**: Structured comment file (.cmt) with MIUVIG information. *(Required)*

## Output
- `<output>.sqn`: The submission file ready for GenBank.
- `<output>.val`: A validation file listing warnings, info, or errors from the submission check.

## Example Usage
```bash
suvtk table2asn -i sequences.fasta -o submission -s source.src -f features.tbl -t template.sbt -c comments.cmt