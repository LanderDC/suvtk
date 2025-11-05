"""
table2asn.py
============

This script generates a .sqn submission file for GenBank. It processes source
and comments files, validates data, and prepares the submission package.

Functions
---------
process_comments(src_file, comments_file)
    Update the comments file based on the source file.

table2asn(input, output, src_file, features, template, comments)
    Main command to generate a .sqn file for GenBank submission.
"""

# TODO: add date correction option
# TODO: check/display stats file for errors (https://www.ncbi.nlm.nih.gov/genbank/validation/#BioSourceMissing) -> OKish
# TODO: add missing required miuvig params from src file? -> comments.py?:  env_broad_scale, env_local_scale, env_medium, investigation_type, project_name, seq_meth
# TODO: add option to make genbank file -> made by default
# TODO: add check for required columns (src, comments)
import rich_click as click

from suvtk import utils


def process_comments(src_file, comments_file):
    """
    Processes comments by updating the comments file based on the source file.

    For each group of isolates, it updates the comments file with:
    - Extra data: `collection_date`, `geo_loc_name`, and `lat_lon` (copied from `Collection_date`,
      `geo_loc_name`, and `Lat_Lon` in the source file).
    - If duplicates exist, it updates:
        - The count of isolates.
        - The majority predicted genome type (taken from the comments file).
        - Sets the predicted genome structure to "segmented".

    Parameters
    ----------
    src_file : str
        The file path to the source file in tab-separated format.
    comments_file : str
        The file path to the comments file in tab-separated format.

    Returns
    -------
    None
    """
    click.echo("Reading source and comments files...")
    src_df = utils.safe_read_csv(src_file, sep="\t")
    comments_df = utils.safe_read_csv(comments_file, sep="\t")

    # Insert extra columns into comments_df after the first column 'StructuredCommentPrefix'
    prefix_col = "StructuredCommentPrefix"
    if prefix_col in comments_df.columns:
        # Find the first occurrence of the prefix column
        first_index = list(comments_df.columns).index(prefix_col)
        cols_to_add = ["collection_date", "geo_loc_name", "lat_lon"]
        for col in cols_to_add:
            if col not in comments_df.columns:
                first_index += 1
                comments_df.insert(first_index, col, "")
                click.echo(f"Inserted column '{col}' after the first '{prefix_col}'.")
    else:
        click.echo(
            f"Warning: '{prefix_col}' not found in comments file. Extra columns will be appended."
        )
        for col in ["collection_date", "geo_loc_name", "lat_lon"]:
            if col not in comments_df.columns:
                comments_df[col] = ""

    click.echo("Grouping source file by 'Isolate'...")
    isolate_groups = src_df.groupby("Isolate")
    total_groups = len(isolate_groups)
    processed_groups = 0

    for isolate, group in isolate_groups:
        processed_groups += 1

        # Get extra data from the first row of the group
        collection_date = group.iloc[0]["Collection_date"]
        geo_loc_name = group.iloc[0]["geo_loc_name"]
        lat_lon = group.iloc[0]["Lat_Lon"]

        # Get the list of Sequence_IDs for the group
        seqids = group["Sequence_ID"].tolist()

        # Update extra fields for each Sequence_ID in this group
        for seqid in seqids:
            comments_df.loc[comments_df["Sequence_ID"] == seqid, "collection_date"] = (
                collection_date
            )
            comments_df.loc[comments_df["Sequence_ID"] == seqid, "geo_loc_name"] = (
                geo_loc_name
            )
            comments_df.loc[comments_df["Sequence_ID"] == seqid, "lat_lon"] = lat_lon

        # If more than one entry exists for this isolate, update duplicate-related fields
        if len(group) > 1:
            isolate_count = len(group)
            click.echo(f"  Found {isolate_count} entries for isolate '{isolate}'.")

            # Compute the majority pred_genome_type from the corresponding rows in comments_df
            subset_comments = comments_df[comments_df["Sequence_ID"].isin(seqids)]
            if (
                not subset_comments.empty
                and "pred_genome_type" in subset_comments.columns
            ):
                majority_genome_type = subset_comments["pred_genome_type"].mode()[0]
                click.echo(
                    f"  Majority 'pred_genome_type' for isolate '{isolate}' is '{majority_genome_type}'."
                )
            else:
                majority_genome_type = "uncharacterized"
                click.echo(
                    f"  No 'pred_genome_type' found for isolate '{isolate}' in comments."
                )

            # Update additional fields for each Sequence_ID in this group
            for seqid in seqids:
                comments_df.loc[
                    comments_df["Sequence_ID"] == seqid, "number_contig"
                ] = isolate_count
                comments_df.loc[
                    comments_df["Sequence_ID"] == seqid, "pred_genome_type"
                ] = majority_genome_type
                comments_df.loc[
                    comments_df["Sequence_ID"] == seqid, "pred_genome_struc"
                ] = "segmented"
        else:
            isolate_count = len(group)
            for seqid in seqids:
                comments_df.loc[
                    comments_df["Sequence_ID"] == seqid, "number_contig"
                ] = isolate_count

    # Rename the duplicate StructuredCommentPrefix column if needed
    comments_df.rename(
        columns={
            "StructuredCommentPrefix.1": "StructuredCommentPrefix",
        },
        inplace=True,
    )
    comments_df.to_csv(comments_file, sep="\t", index=False)
    click.echo("Comments file updated and saved.")


@click.command(short_help="Generate .sqn submission for Genbank.")
@click.option(
    "-i",
    "--input",
    "input",
    required=True,
    type=click.Path(exists=True),
    help="Input fasta file",
)
@click.option(
    "-o",
    "--output",
    "output",
    required=True,
    type=click.Path(exists=False),
    help="Output prefix",
)
@click.option(
    "-s",
    "--src-file",
    "src_file",
    required=True,
    type=click.Path(exists=True),
    help="File with Source modifiers (.src).",
)
@click.option(
    "-f",
    "--features",
    "features",
    required=True,
    type=click.Path(exists=True),
    help="Feature table file (.tbl).",
)
@click.option(
    "-t",
    "--template",
    "template",
    required=True,
    type=click.Path(exists=True),
    help="Template file with author information (.sbt). See https://submit.ncbi.nlm.nih.gov/genbank/template/submission/",
)
@click.option(
    "-c",
    "--comments",
    "comments",
    required=True,
    type=click.Path(exists=True),
    help="Structured comment file (.cmt) with MIUVIG information.",
)
def table2asn(input, output, src_file, features, template, comments):
    """This command generates a .sqn file that you can send to gb-sub@ncbi.nlm.nih.gov"""

    # Process the comments file based on the src_file
    process_comments(src_file, comments)

    Cmd = "table2asn "
    Cmd += f"-i {input} "
    Cmd += f"-o {output}.sqn "
    Cmd += f"-t {template} "
    Cmd += f"-f {features} "
    Cmd += f"-src-file {src_file} "
    Cmd += f"-w {comments} "
    Cmd += "-V vb "  # Check for errors
    Cmd += "-a s"  # allow multifasta file

    utils.Exec(Cmd, raise_on_error=False)

    tag = 0
    error_file = f"{output}.val"
    with open(error_file, "r") as f:
        for line in f.readlines():
            if line.startswith("Warning") or line.startswith("Info"):
                # click.echo(f"{line}")
                continue
            else:
                click.echo(f"UNEXPECTED ERROR -- {line}")
                tag = 1

    if tag == 0:
        print("No major errors reported for Genbank submission")
