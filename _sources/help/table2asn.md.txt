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
Example:
| Sequence_ID                              | Organism              | Isolate          | Collection_date | geo_loc_name | Metagenome_source    | Lat_Lon             | Biosample    | SRA         | Segment | Metagenomic |
|------------------------------------------|-----------------------|------------------|-----------------:|--------------|----------------------|---------------------|--------------|-------------|---------:|-------------|
| NODE_A73_length_3582_cov_43.001141_BlackFly36 | Riboviria&nbsp;sp.         | BlackFly36_bazTh | Jul-21          | Cameroon     | blackfly metagenome  | 4.352433&nbsp;N&nbsp;11.63255&nbsp;E | SAMN40472428 | SRR28387197 |         | TRUE        |
| NODE_A75_length_3505_cov_41.815636_BlackFly36 | Chrysoviridae&nbsp;sp.     | BlackFly36_8xzwR | Jul-21          | Cameroon     | blackfly metagenome  | 4.352433&nbsp;N&nbsp;11.63255&nbsp;E | SAMN40472428 | SRR28387197 |         | TRUE        |
| NODE_A83_length_3264_cov_59.004079_BlackFly36 | unclassified&nbsp;viruses  | BlackFly36_xliVj | Jul-21          | Cameroon     | blackfly metagenome  | 4.352433&nbsp;N&nbsp;11.63255&nbsp;E | SAMN40472428 | SRR28387197 |         | TRUE        |
| NODE_A87_length_3161_cov_62.407912_BlackFly36 | Chrysoviridae&nbsp;sp.     | BlackFly36_qC6AD | Jul-21          | Cameroon     | blackfly metagenome  | 4.352433&nbsp;N&nbsp;11.63255&nbsp;E | SAMN40472428 | SRR28387197 |    1    | TRUE        |
| NODE_A94_length_3096_cov_54.536933_BlackFly36 | Chrysoviridae&nbsp;sp.     | BlackFly36_M1XGF | Jul-21          | Cameroon     | blackfly metagenome  | 4.352433&nbsp;N&nbsp;11.63255&nbsp;E | SAMN40472428 | SRR28387197 |    2    | TRUE        |
| NODE_A96_length_3065_cov_54.700469_BlackFly36 | Chrysoviridae&nbsp;sp.     | BlackFly36_M0xJc | Jul-21          | Cameroon     | blackfly metagenome  | 4.352433&nbsp;N&nbsp;11.63255&nbsp;E | SAMN40472428 | SRR28387197 |    3    | TRUE        |
| NODE_A102_length_2949_cov_37.451950_BlackFly36 | Chrysoviridae&nbsp;sp.     | BlackFly36_T0QlA | Jul-21          | Cameroon     | blackfly metagenome  | 4.352433&nbsp;N&nbsp;11.63255&nbsp;E | SAMN40472428 | SRR28387197 |    4    | TRUE        |
| NODE_A254_length_1010_cov_2.266881_BlackFly24 | Negarnaviricota&nbsp;sp.   | BlackFly24_IowNh | Jul-21          | Cameroon     | blackfly metagenome  | 4.352433&nbsp;N&nbsp;11.63255&nbsp;E | SAMN40472416 | SRR28387210 |         | TRUE        |
| NODE_A8_length_3774_cov_333.669191_BlackFly25 | Riboviria&nbsp;sp.         | BlackFly25_o7K62 | Jul-21          | Cameroon     | blackfly metagenome  | 4.352433&nbsp;N&nbsp;11.63255&nbsp;E | SAMN40472417 | SRR28387209 |         | TRUE        |

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