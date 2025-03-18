# comments
---
## Overview
This command generates a <a href="https://www.ncbi.nlm.nih.gov/genbank/structuredcomment/" target="_blank">structured comment</a> file based on MIUVIG standards. It merges taxonomy, features, MIUVIG, and assembly data into a unified output file that will add structured comments to the GenBank submission.

### MIUVIG structured comment
#### MIUVIG taxonomy
The `--taxonomy` file should contain info on the genome structure and type of your viral sequences. These are mandatory parameters in the MIUVIG standard and can be obtained with the [`suvtk virus-info`](virus-info.md) if you determined your own taxonomy, or [`suvtk taxonomy`](taxonomy.md) to get both the taxonomy and predicted genome structure and type for your sequences. These commands will output `miuvig_taxonomy.tsv` containing this info for all sequences.

```{dropdown} Example

| contig | pred_genome_type | pred_genome_struc |
|--------|------------------|-------------------|
| Seq1 | uncharacterized | undetermined |
| Seq2 | ssRNA(+) | non-segmented |
| Seq3 | uncharacterized | undetermined |
| Seq4 | dsRNA | segmented |
```

#### MIUVIG features
The `--features` input file should contain info on the software, database and method that is used to annotate the features in your viral sequences. The [`suvtk features`](features.md) generates `miuvig_features.tsv` containing all tool and databases with their versions and parameters used by `suvtk`.

```{dropdown} Example

| MIUVIG_parameter  | value                                              |
|-------------------|----------------------------------------------------|
| feat_pred         | pyrodigal-gv;0.3.2;-g 1, default otherwise         |
| ref_db            | BFVD;2023_02;https://bfvd.steineggerlab.workers.dev |
| sim_search_meth   | MMseqs2;17.b804f;-s 7.5, default otherwise         |
```

#### Global MIUVIG parameters
The MIUVIG tsv file should contain global parameters of your study that apply to all your sequences. It should be a tsv file with two columns: *MIUVIG_parameter* and *value*. Allowed parameters and their values, including which parameters are mandatory, can be found [here](https://static-content.springer.com/esm/art%3A10.1038%2Fnbt.4306/MediaObjects/41587_2019_BFnbt4306_MOESM36_ESM.xlsx) and the corresponding MIUVIG_parameter strings can be found <a href="https://genomicsstandardsconsortium.github.io/mixs/0010012/" target="_blank">here</a>.

```{dropdown} Example
:open:

| MIUVIG_parameter     | value                                                                 |
|----------------------|-----------------------------------------------------------------------|
| source_uvig          | viral fraction metagenome (virome)                                    |
| assembly_software    | metaSPAdes;v3.15.3;kmer set 21,33,55,77, default otherwise            |
| vir_ident_software   | genomad;1.7.0;score-calibration, default otherwise                    |
| size_frac            | 0-0.8 um                                                              |
| virus_enrich_appr    | filtration + centrifugation + DNAse + RNAse                           |
| nucl_acid_ext        | 10.1038/srep16532                                                     |
| wga_amp_appr         | mda based                                                             |
```

#### CheckV quality_summary.tsv
Providing the `quality_summary.tsv` output of <a href="https://bitbucket.org/berkeleylab/checkv/src/master/" target="_blank">CheckV</a> is optional, but will add more information in the MIUVIG structured comment. For example, the quality will be taken from CheckV's quality estimation (High-quality or Genome-fragment) and also the completeness score will be added. Also if the sequence is a provirus (UpViG) will be taken into account. If you do not provide this file, sequences are considered to be 'Genome fragment(s)' and 'independent sequence (UViG) by default.

```{note}
Providing the `quality_summary.tsv` CheckV file will be mostly useful when you have bacteriophage sequences as CheckV can not reliably estimate the completeness score for eukaryotic (RNA) viruses.
```
---
### Assembly comment
The assembly comment file is essentially a tsv file that contains the necessary information on the Assembly structured comment. It should again contain two columns: *Assembly_parameter* and *value*. There are three possible *Assembly_parameter* values: *StructuredCommentPrefix* which should always be *Assembly-Data*, *Assembly Method* which contains the assembly software you used and *Sequencing Technology* which should include the sequencing platform used to generate your data.

```{dropdown} Example
:open:

| Assembly_parameter       | value                    |
|--------------------------|--------------------------|
| StructuredCommentPrefix  | Assembly-Data            |
| Assembly Method          | metaSPAdes v. 3.15.3     |
| Sequencing Technology    | Illumina NovaSeq 6000    |
```

---
## Required Input
- **-t, -\\\-taxonomy**: MIUVIG TSV file produced by the `taxonomy` subcommand. *(Required)*
- **-f, -\\\-features**: MIUVIG TSV file produced by the `features` subcommand. *(Required)*
- **-m, -\\\-miuvig**: TSV file containing MIUVIG information. *(Required)*
- **-a, -\\\-assembly**: TSV file with GenBank assembly information. *(Required)*
- **-o, -\\\-output**: Output filename (the script appends `.cmt` to the provided name). *(Required)*

## Optional Parameters
- **-c, -\\\-checkv**: CheckV's quality_summary.tsv file.

## Output
- A structured comment file (e.g., `output.cmt`) that consolidates various data fields and meets MIUVIG standards.

## Example Usage
```bash
suvtk comments -t taxonomy.tsv -f features.tsv -m miuvig.tsv -a assembly.tsv -o structured_comment
