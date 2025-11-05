"""
virus_info.py
=============

This script provides information on potentially segmented viruses based on their taxonomy.
It also outputs genome type and structure information for MIUVIG structured comments.

Functions
---------
load_segment_db()
    Load the segmented viruses database.

load_genome_type_db()
    Load the genome structure database.

run_segment_info(tax_df, database, output_path)
    Process taxonomy data to extract segmented virus and genome type information.

virus_info(taxonomy, database, output_path)
    Main command to analyze segmented viruses and generate genome type information.
"""

# TODO: Rename to genome_info?
import importlib.resources
import os
from pathlib import Path

import pandas as pd
import rich_click as click
import taxopy

from suvtk import utils


def load_segment_db():
    """
    Load the segmented viruses database.

    Returns
    -------
    pandas.DataFrame
        Data frame with the segmented viruses database.
    """
    with (
        importlib.resources.files("suvtk.data")
        .joinpath("segmented_viruses.tsv")
        .open("r") as file
    ):
        db = utils.safe_read_csv(file, sep="\t", header=0)
        return db


def load_genome_type_db():
    """
    Load the genome structure database.

    Returns
    -------
    pandas.DataFrame
        Data frame with the genome structure database.
    """
    with (
        importlib.resources.files("suvtk.data")
        .joinpath("genome_types.tsv")
        .open("r") as file
    ):
        db = utils.safe_read_csv(file, sep="\t", header=0)
        return db


def run_segment_info(tax_df, database, output_path):
    """
    Process the taxonomy file to get segmented virus and genome type info.

    Parameters
    ----------
    tax_df : pandas.DataFrame
        Pandas DataFrame with taxonomy information.
    database : str
        The suvtk database path (contains nodes.dmp, names.dmp, etc.).
    output_path : str
        The output directory where results will be saved.

    Returns
    -------
    None
    """

    # Load segmented viruses and genome structure databases.
    segment_db = load_segment_db()
    genome_type_db = load_genome_type_db()

    # Load taxonomy database from the given database path.
    taxdb = taxopy.TaxDb(
        nodes_dmp=os.path.join(database, "nodes.dmp"),
        names_dmp=os.path.join(database, "names.dmp"),
    )

    results = []  # For segmented virus details from segment_db
    gt_results = []  # For genome type records from genome_type_db
    segmented = False  # Flag to trigger extra messages

    for index, row in tax_df.iterrows():
        if row["taxonomy"] == "unclassified viruses":
            gt_results.append(
                {
                    "contig": row["contig"],
                    "pred_genome_type": "uncharacterized",
                    "pred_genome_struc": "undetermined",
                }
            )
            continue

        # Remove trailing " sp." before lookup.
        tax = row["taxonomy"].removesuffix(" sp.")
        try:
            taxid = taxopy.taxid_from_name(tax, taxdb)
            lineage = taxopy.Taxon(taxid[0], taxdb).name_lineage
        except IndexError:
            click.echo(
                f"Warning: '{tax}' is not part of the official ICTV taxonomy. "
                f"Genome type and structure cannot be accessed for {row['contig']}."
            )
            gt_results.append(
                {
                    "contig": row["contig"],
                    "pred_genome_type": "uncharacterized",
                    "pred_genome_struc": "undetermined",
                }
            )
            continue

        segment_record = None
        genome_type_record = None

        # Loop once over the lineage to get both records.
        for taxa in lineage:
            if segment_record is None and taxa in segment_db["taxon"].values:
                segment_record = (
                    segment_db.loc[segment_db["taxon"] == taxa].iloc[0].to_dict()
                )
                record = {"contig": row["contig"], **segment_record}
                results.append(record)
                if float(segment_record["segmented_fraction"]) >= 25:
                    segmented = True
                    click.echo(
                        f"\n{row['contig']} is part of the {segment_record['taxon']} {segment_record['rank']}, "
                        f"{float(segment_record['segmented_fraction']):.2f}% are segmented viruses."
                    )
                    if segment_record["min_segment"] != segment_record["max_segment"]:
                        click.echo(
                            f"Most viruses of {segment_record['taxon']} have "
                            f"{segment_record['majority_segment']} segments, but it may vary between "
                            f"{segment_record['min_segment']} and {segment_record['max_segment']}."
                        )
                    else:
                        click.echo(
                            f"The segmented viruses of {segment_record['taxon']} have "
                            f"{segment_record['majority_segment']} segments."
                        )
            if genome_type_record is None and taxa in genome_type_db["taxon"].values:
                genome_type_record = (
                    genome_type_db.loc[genome_type_db["taxon"] == taxa]
                    .iloc[0]
                    .to_dict()
                )

            if segment_record is not None and genome_type_record is not None:
                break

        if segment_record is not None:
            try:
                seg_frac = float(segment_record["segmented_fraction"])
            except (ValueError, TypeError):
                seg_frac = 0.0
            if seg_frac == 100:
                pred_struc = "segmented"
            elif seg_frac > 0:
                pred_struc = "undetermined"
            else:
                pred_struc = "non-segmented"
        else:
            pred_struc = "non-segmented"

        if genome_type_record is not None:
            genome_type_record.pop("taxon")
            genome_type_record["contig"] = row["contig"]
            genome_type_record["pred_genome_struc"] = pred_struc
            gt_results.append(genome_type_record)
        else:
            gt_results.append(
                {
                    "contig": row["contig"],
                    "pred_genome_type": "uncharacterized",
                    "pred_genome_struc": "undetermined",
                }
            )

    genome_type_df = pd.DataFrame(gt_results)[
        ["contig", "pred_genome_type", "pred_genome_struc"]
    ]
    genome_type_df.to_csv(
        os.path.join(output_path, "miuvig_taxonomy.tsv"), sep="\t", index=False
    )

    if segmented:
        click.echo("\nYou might want to check your data for missing segments.")
    if results:
        segmented_df = pd.DataFrame(results).sort_values(
            by="segmented_fraction", ascending=False
        )
        segmented_df.to_csv(
            os.path.join(output_path, "segmented_viruses_info.tsv"),
            sep="\t",
            index=False,
        )
        click.echo(
            "\nContig information on segmented viruses written to 'segmented_viruses_info.tsv'."
        )


@click.command(
    short_help="Get information on possible segmented viruses based on their taxonomy."
)
@click.option(
    "--taxonomy",
    required=True,
    type=click.Path(exists=True),
    help="Taxonomy file.",
)
@click.option(
    "-d",
    "--database",
    "database",
    required=True,
    type=click.Path(exists=True),
    help="The suvtk database path.",
)
@click.option(
    "-o",
    "--output",
    "output_path",
    required=True,
    type=click.Path(exists=False),
    help="Output directory",
)
def virus_info(taxonomy, database, output_path):
    """
    This command provides info on potentially segmented viruses based on the taxonomy and also outputs a file with the genome type and genome structure for the MIUVIG structured comment.
    """
    if os.path.exists(output_path):
        click.echo(
            f"Warning: Output directory '{output_path}' already exists and will be overwritten."
        )
    os.makedirs(output_path, exist_ok=True)

    tax_df = utils.safe_read_csv(taxonomy, sep="\t")
    run_segment_info(tax_df, database, output_path)


if __name__ == "__main__":
    virus_info()
