"""
taxonomy.py
===========

This script assigns taxonomy to sequences using MMseqs2 from the ICTV nr database.
It generates taxonomy files and integrates with other modules for further processing.

Functions
---------
taxonomy(fasta_file, database, output_path, seqid, threads)
    Main command to assign taxonomy to sequences.
"""

# TODO: save MIUVIG file with pred_genome_type and pred_genome_struc
# TODO: Change to genomad taxonomy
# TODO: mmseqs overwrite tmp file (mmseqs fails when command was previously aborted)
import os
import re
import shutil

import click
import pandas as pd
import psutil

from suvtk import utils, virus_info


def parse_memlimit(mem_str):
    """
    Parse memory string like '30G', '40000M', '32GB' into bytes.
    Returns an integer number of bytes.
    """
    mem_str = mem_str.strip().upper()
    match = re.match(r"(\d+(?:\.\d+)?)([GMK]?)B?$", mem_str)
    if not match:
        raise ValueError(f"Invalid memory limit format: '{mem_str}'")

    value, unit = match.groups()
    value = float(value)
    if unit == "G":
        value *= 1024**3
    elif unit == "M":
        value *= 1024**2
    elif unit == "K":
        value *= 1024
    # default = bytes
    return int(value)


@click.command(short_help="Assign virus taxonomy to sequences.")
@click.option(
    "-i",
    "--input",
    "fasta_file",
    required=True,
    type=click.Path(exists=True),
    help="Input fasta file",
)
@click.option(
    "-o",
    "--output",
    "output_path",
    required=True,
    type=click.Path(exists=False),
    help="Output directory",
)
@click.option(
    "-d",
    "--database",
    "database",
    required=True,
    type=click.Path(exists=True),
    help="Path to the suvtk database folder.",
)
@click.option(
    "-s",
    "--identity",
    "seqid",
    required=False,
    default=0.7,
    type=float,
    help="Minimum sequence identity for hits to be considered",
)
@click.option(
    "-t",
    "--threads",
    "threads",
    required=False,
    default=utils.get_available_cpus(),
    type=int,
    help="Number of threads to use",
)
@click.option(
    "--memory-limit",
    "memlimit",
    required=False,
    default=None,
    type=str,
    help="Memory limit for MMseqs2 (e.g. 4G, 2000M). Defaults to available system memory.",
)
def taxonomy(fasta_file, database, output_path, seqid, threads, memlimit):
    """
    This command uses MMseqs2 to assign taxonomy to sequences using protein sequences from ICTV taxa in the nr database.
    """
    if os.path.exists(output_path):
        click.echo(
            f"Warning: Output directory '{output_path}' already exists and will be overwritten."
        )

    os.makedirs(output_path, exist_ok=True)

    taxresult_path = os.path.join(output_path, "taxresults")

    # TODO Add RAM restrictions? need at least 30G add split-memory-limit for limited systems
    # TODO Add error handling
    # TODO removing tmp before running mmseqs might be dangerous
    if os.path.exists("tmp"):
        shutil.rmtree("tmp")

    # Auto-detect memory if not provided
    if not memlimit:
        total_mem_gb = psutil.virtual_memory().available / (1024**3)
        # Leave a little headroom
        memlimit = f"{int(total_mem_gb) - 1}G"

    # Validate memory limit (at least 30G)
    try:
        mem_bytes = parse_memlimit(memlimit)
    except ValueError as e:
        raise click.BadParameter(str(e))

    if mem_bytes < 30 * 1024**3:
        raise click.BadParameter(
            f"Memory limit too low ({memlimit}). Must be at least 30G."
        )

    Cmd = "mmseqs easy-taxonomy "
    Cmd += f"{fasta_file} "  # input
    Cmd += os.path.join(database, "ictv_nr_db") + " "  # database
    Cmd += f"{taxresult_path} "  # output
    Cmd += "tmp "  # tmp
    Cmd += "-s 7.5 --blacklist '' --tax-lineage 1 "
    Cmd += f"--threads {threads} "
    Cmd += f"--split-memory-limit {memlimit} "
    utils.Exec(Cmd)

    shutil.rmtree("tmp")

    taxonomy = utils.safe_read_csv(f"{taxresult_path}_lca.tsv", sep="\t", header=None)
    taxonomy.rename(
        {
            0: "query",
            1: "taxid",
            2: "rank",
            3: "name",
            4: "fragments",
            5: "assigned",
            6: "agreement",
            7: "support",
            8: "lineage",
        },
        axis=1,
        inplace=True,
    )

    tophit = utils.safe_read_csv(f"{taxresult_path}_tophit_aln", sep="\t", header=None)
    tophit.rename(
        {
            0: "query",
            1: "target",
            2: "pident",
            3: "len",
            4: "mismatch",
            5: "gapopen",
            6: "qstart",
            7: "qend",
            8: "tstart",
            9: "tend",
            10: "evalue",
            11: "bits",
        },
        axis=1,
        inplace=True,
    )

    # Select top hits
    highest_bits_idx = tophit.groupby("query")["bits"].idxmax()
    top_tophit = tophit.loc[highest_bits_idx]

    merged = pd.merge(taxonomy, top_tophit, on="query", how="left")

    tax_names = []
    for index, row in merged.iterrows():
        if row["rank"] == "no rank":
            click.echo(f"No taxonomy for {row['query']}")
            last_known = "unclassified viruses"
        elif row["rank"] == "species":  # Fix issue when species contains sp.
            last_known = row["lineage"].split(";")[-2].replace("g_", "")
            last_known += " sp."
        elif (
            row["rank"] == "genus" and row["pident"] < seqid  # TODO check best cutoff
        ):  # if genus rank and sequence identity is lower than 70% (seqid) get family assignment
            last_known = row["lineage"].split(";")[-2].replace("f_", "")
            last_known += " sp."
        else:
            last_known = row["name"].strip()
            last_known += " sp."
        tax_names.append(
            [
                row["query"],
                last_known,
            ]
        )

    tax_df = pd.DataFrame(tax_names, columns=["contig", "taxonomy"])
    tax_df.to_csv(os.path.join(output_path, "taxonomy.tsv"), sep="\t", index=False)

    virus_info.run_segment_info(tax_df, database, output_path)


if __name__ == "__main__":
    taxonomy()
