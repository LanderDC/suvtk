# comments

## Overview
This command generates a <a href="https://www.ncbi.nlm.nih.gov/genbank/structuredcomment/" target="_blank">structured comment</a> file based on MIUVIG standards. It merges taxonomy, features, MIUVIG, and assembly data into a unified output file that will add structured comments to the GenBank submission.

### MIUVIG tsv
The MIUVIG tsv file should contain global parameters of your study that apply to all your sequences. It should be a tsv file with two columns: *MIUVIG_parameter* and *value*. The following parameters are mandatory and their allowed values can be found [here](https://static-content.springer.com/esm/art%3A10.1038%2Fnbt.4306/MediaObjects/41587_2019_BFnbt4306_MOESM36_ESM.xlsx).

```{admonition} Example

| MIUVIG_parameter     | value                                                                 |
|----------------------|-----------------------------------------------------------------------|
| source_uvig          | viral fraction metagenome (virome)                                    |
| assembly_software    | metaSPAdes;v3.15.3;kmer set 21,33,55,77, default otherwise            |
| vir_ident_software   | genomad;1.7.0;score-calibration, default otherwise                    |
| detec_type           | independent sequence (UViG)                                           | # Get this from CheckV file
| assembly_qual        | Genome fragment(s)                                                    | # Get this from CheckV file
| number_contig        | 1                                                                     | # possibly remove this (see isolate count table2asn script)
| size_frac            | 0-0.8 um                                                              |
| virus_enrich_appr    | filtration + centrifugation + DNAse + RNAse                           |
| nucl_acid_ext        | 10.1038/srep16532                                                     |
| wga_amp_appr         | mda based                                                             |
```

### Assembly comment
The assembly comment file is essentially a tsv file that contains the necessary information on the Assembly structured comment. It should again contain two columns: *Assembly_parameter* and *value*. There are three possible *Assembly_parameter* values: *StructuredCommentPrefix* which should always be *Assembly-Data*, *Assembly Method* which contains the assembly software you used and *Sequencing Technology* which should include the sequencing platform used to generate your data.

```{admonition} Example

| Assembly_parameter       | value                    |
|--------------------------|--------------------------|
| StructuredCommentPrefix  | Assembly-Data            |
| Assembly Method          | metaSPAdes v. 3.15.3     |
| Sequencing Technology    | Illumina NovaSeq 6000    |
```

## Required Input
- **-t, -\\\-taxonomy**: MIUVIG TSV file produced by the `taxonomy` subcommand. *(Required)*
- **-f, -\\\-features**: MIUVIG TSV file produced by the `features` subcommand. *(Required)*
- **-m, -\\\-miuvig**: TSV file containing MIUVIG information. *(Required)*
- **-a, -\\\-assembly**: TSV file with GenBank assembly information. *(Required)*
- **-o, -\\\-output**: Output filename (the script appends `.cmt` to the provided name). *(Required)*

## Output
- A structured comment file (e.g., `output.cmt`) that consolidates various data fields and meets MIUVIG standards.

## Example Usage
```bash
suvtk comments -t taxonomy.tsv -f features.tsv -m miuvig.tsv -a assembly.tsv -o structured_comment
