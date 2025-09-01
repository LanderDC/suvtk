"""
co_occurrence.py
================

This script identifies co-occurring sequences in an abundance table based on
prevalence and correlation thresholds. It supports optional segment-specific
analysis and contig length correction.

Functions
---------
calculate_proportion(df)
    Calculate the proportion of samples for each contig.

create_correlation_matrix(df_transposed)
    Generate a Spearman correlation matrix and mask the upper triangle.

segment_correlation_matrix(df, segment_list)
    Calculate correlations for specific segments with all rows in the DataFrame.

create_segment_list(segment_file)
    Read a file containing segment identifiers and return them as a list.

co_occurrence(input, output, segments, lengths, prevalence, correlation, strict)
    Main command to identify co-occurring sequences in an abundance table.
"""

import sys
from pathlib import Path

import click
import numpy as np
import pandas as pd


def calculate_proportion(df):
    """
    Calculate the proportion of samples for each contig in a dataframe.

    Parameters
    ----------
    df : pandas.DataFrame
        A pandas DataFrame where rows represent contigs and columns represent samples.

    Returns
    -------
    pandas.DataFrame
        The original DataFrame with two additional columns: 'sample_count', the total number of samples a contig is present in, and 'proportion_samples', the proportion of samples a contig is present in.
    """
    df["sample_count"] = df.apply(lambda row: row[row != 0].count(), axis=1)
    df["proportion_samples"] = df["sample_count"] / (df.shape[1] - 1)

    return df


def create_correlation_matrix(df_transposed):
    """
    Calculate a Spearman correlation matrix for the transposed dataframe and mask the upper triangle.

    Parameters
    ----------
    df_transposed : pandas.DataFrame
        A transposed pandas DataFrame where rows represent samples and columns represent variables.

    Returns
    -------
    pandas.DataFrame
        A masked correlation matrix with the upper triangle set to NaN, and the axes renamed to 'Contig1' and 'Contig2'.
    """

    correlation_matrix = df_transposed.corr(method="spearman")

    mask = np.triu(np.ones(correlation_matrix.shape), k=1).astype(bool)
    masked_correlation_matrix = correlation_matrix.mask(mask)

    correlation_matrix = masked_correlation_matrix.rename_axis(
        axis=0, mapper="Contig1"
    ).rename_axis(axis=1, mapper="Contig2")

    return correlation_matrix


def segment_correlation_matrix(df, segment_list):
    """
    Calculate the correlation of each segment in the segment list with all rows in the DataFrame.

    Parameters
    ----------
    df : pandas.DataFrame
        A pandas DataFrame with rows representing samples and columns representing variables.
    segment_list : list
        A list of segment indices to calculate correlations with.

    Returns
    -------
    pandas.DataFrame
        A DataFrame where each column represents a segment from the segment_list and each value
        is the Spearman correlation with the corresponding row in the original DataFrame.
    """

    correlation_results_df = pd.DataFrame()

    # Loop through each segment in segment_list
    for i in segment_list:
        df2 = df.loc[i]
        df3 = df.corrwith(df2, axis=1, method="spearman")

        # Append the results to the DataFrame with i as the column name
        correlation_results_df[i] = df3

    return correlation_results_df


def create_segment_list(segment_file):
    """
    Reads a file containing segment identifiers and returns them as a list.

    Parameters
    ----------
    segment_file : str
        The path to a file containing segment identifiers, one per line.

    Returns
    -------
    list
        A list of segment identifiers with whitespace stripped.
    """

    file_path = Path(segment_file)

    # Read the file into a list
    with open(file_path, "r") as file:
        segment_list = file.readlines()

    segment_list = [line.strip() for line in segment_list]
    return segment_list


@click.command(short_help="Find co-occurring sequences in abundance table.")
@click.option(
    "-i",
    "--input",
    "input",
    type=click.Path(exists=True),
    metavar="FILE",
    required=True,
    help="Abundance table file (tsv).",
)
@click.option(
    "-o",
    "--output",
    "output",
    type=str,
    metavar="OUTPUT",
    required=True,
    help="Prefix for the output name.",
)
@click.option(
    "-s",
    "--segments",
    "segments",
    type=str,
    metavar="FILE",
    help="File with a list of contigs of interest (often RdRP segments), each on a new line.",
)
@click.option(
    "-l",
    "--lengths",
    "lengths",
    type=str,
    metavar="FILE",
    help="File with the lengths of each contig.",
)
@click.option(
    "-p",
    "--prevalence",
    "prevalence",
    type=float,
    metavar="FLOAT",
    default=0.1,
    help="Minimum percentage of samples for correlation analysis.",
)
@click.option(
    "-c",
    "--correlation",
    "correlation",
    type=float,
    metavar="FLOAT",
    default=0.5,
    help="Minimum correlation to keep pairs.",
)
@click.option(
    "--strict",
    is_flag=True,
    default=False,
    help="The correlation threshold should be met for all provided segments.",
)
def co_occurrence(input, output, segments, lengths, prevalence, correlation, strict):
    """
    Identify co-occurring sequences in an abundance table based on specified thresholds.

    This function reads an abundance table, filters contigs based on prevalence, and calculates
    correlation matrices to identify co-occurring sequences. It supports optional segment-specific
    analysis and contig length correction.
    """

    click.echo("Read in abundance table.")
    abundance_df = pd.read_csv(input, sep="\t", index_col=0)
    df = calculate_proportion(abundance_df)

    # Define the threshold
    prevalence_threshold = prevalence

    # Filter rows where the proportion of 0s is less than or equal to the threshold
    filtered_df = df[df["proportion_samples"] >= prevalence_threshold].drop(
        ["sample_count", "proportion_samples"], axis=1
    )

    n = len(filtered_df)

    if lengths:
        click.echo("Using contig length corrected abundance table.")
        lengths = pd.read_csv(
            lengths, sep="\t", index_col=0, header=None, names=["Contig", "length"]
        )
        df = filtered_df.div(lengths["length"], axis=0).dropna(how="all")
    else:
        click.echo("Using absence/presence abundance table.")
        df = filtered_df.map(lambda x: 1 if x > 0 else x)

    click.echo(
        f"Calculate correlation matrix for {n} contigs (contig prevalence in samples set to {prevalence_threshold*100}%)."
    )

    cor_threshold = correlation

    if segments:
        segment_list = create_segment_list(segments)

        # Check if all values in segment_list are present in df indices
        missing_segments = [
            segment for segment in segment_list if segment not in df.index
        ]

        if missing_segments:
            missing_segments_str = ", ".join(map(str, missing_segments))
            click.echo(
                f"Error: The following segment(s) are not present in the sample prevalence filtered abundance table: {missing_segments_str}\n"
                f"Consider lowering the prevalence threshold (-p) which is currently at {prevalence_threshold}"
            )
            sys.exit(1)

        correlation_results_df = segment_correlation_matrix(df, segment_list)

        if strict:
            mask = (correlation_results_df >= cor_threshold).all(axis=1)
        else:
            mask = (correlation_results_df >= cor_threshold).any(axis=1)

        corr_df = correlation_results_df[mask]

        click.echo(f"Write correlation matrix with a threshold of {cor_threshold}")
        corr_df.to_csv(output + ".tsv", sep="\t", index=True)
    else:
        df_transposed = df.transpose()
        correlation_matrix = create_correlation_matrix(df_transposed)

        click.echo("Write correlation matrix.")
        correlation_matrix.to_csv(
            output + "_correlation_matrix.tsv", sep="\t", index=True
        )

        click.echo("Write pairwise dataframe.")

        related_contigs = correlation_matrix[
            correlation_matrix >= cor_threshold
        ].stack()

        result_df = pd.DataFrame(related_contigs)
        result_df = result_df.reset_index()

        # Rename existing columns if necessary
        result_df.columns = ["Contig1", "Contig2", "Correlation"]
        result_df = result_df[result_df["Contig1"] != result_df["Contig2"]]

        result_df.sort_values(by="Contig1", inplace=True)
        result_df.to_csv(output + "_related_contigs.tsv", sep="\t", index=False)

    click.echo("Finished.")


if __name__ == "__main__":
    co_occurrence()
