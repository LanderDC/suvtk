import click
import pandas as pd
import os

# Allowed value lists for various parameters
uvig_source_allowed = [
    "metagenome (not viral targeted)",
    "viral fraction metagenome (virome)",
    "sequence-targeted metagenome",
    "metatranscriptome (not viral targeted)",
    "viral fraction RNA metagenome (RNA virome)",
    "sequence-targeted RNA metagenome",
    "microbial single amplified genome (SAG)",
    "viral single amplified genome (vSAG)",
    "isolate microbial genome",
    "other",
]

pred_genome_type_allowed = [
    "DNA",
    "dsDNA",
    "ssDNA",
    "RNA",
    "dsRNA",
    "ssRNA",
    "ssRNA(+)",
    "ssRNA(-)",
    "mixed",
    "uncharacterized",
]

pred_genome_struc_allowed = [
    "segmented",
    "non-segmented",
    "undetermined",
]

detec_type_allowed = [
    "independent sequence (UViG)",
    "provirus (UpViG)",
]

assembly_qual_allowed = [
    "Finished genome",
    "High-quality draft genome",
    "Genome fragment(s)",
]

virus_enrich_appr_allowed = [
    "filtration",
    "ultrafiltration",
    "centrifugation",
    "ultracentrifugation",
    "PEG Precipitation",
    "FeCl Precipitation",
    "CsCl density gradient",
    "DNAse",
    "RNAse",
    "targeted sequence capture",
    "other",
    "none",
]

wga_amp_appr_allowed = [
    "pcr based",
    "mda based",
    "none",
]

# For parameters that come from the merged files (features and miuvig)
# we expect them to be one of the following allowed values (if present).
allowed_values = {
    "source_uvig": uvig_source_allowed,
    "detec_type": detec_type_allowed,
    "assembly_qual": assembly_qual_allowed,
    "virus_enrich_appr": virus_enrich_appr_allowed,
    "wga_amp_appr": wga_amp_appr_allowed,
    # Note: pred_genome_type and pred_genome_struc come from the taxonomy file
    # and are checked separately.
}


@click.command(short_help="Generate structured comment file based on MIUVIG standards.")
@click.option(
    "-t",
    "--taxonomy",
    "taxonomy",
    required=True,
    type=click.Path(exists=True),
    help="MIUVIG TSV file generated by the `taxonomy` subcommand.",
)
@click.option(
    "-f",
    "--features",
    "features",
    required=True,
    type=click.Path(exists=True),
    help="MIUVIG TSV file generated by the `features` subcommand.",
)
@click.option(
    "-m",
    "--miuvig",
    "miuvig",
    required=True,
    type=click.Path(exists=True),
    help="TSV file with MIUVIG information.",
)
@click.option(
    "-o",
    "--output",
    "output",
    required=True,
    type=click.Path(exists=False),
    help="Output filename.",
)
# @click.option(
#    "--assembly-software",
#    required=True,
#    type=str,
#    help="",
# )
# @click.option(
#    "--seq-technology",
#    required=True,
#    type=str,
#    help="",
# )
def comments(taxonomy, features, miuvig, output):
    # 1. Read the taxonomy file.
    taxonomy_df = pd.read_csv(taxonomy, sep="\t")

    # 2. Early check of taxonomy file columns (these come from taxonomy file itself)
    # Check pred_genome_type
    if "pred_genome_type" in taxonomy_df.columns:
        invalid = taxonomy_df[
            ~taxonomy_df["pred_genome_type"].isin(pred_genome_type_allowed)
        ]
        if not invalid.empty:
            invalid_vals = ", ".join(map(str, invalid["pred_genome_type"].unique()))
            raise click.ClickException(
                f"Invalid value(s) in column 'pred_genome_type': {invalid_vals}. Allowed values: {', '.join(pred_genome_type_allowed)}."
            )
    # Check pred_genome_struc
    if "pred_genome_struc" in taxonomy_df.columns:
        invalid = taxonomy_df[
            ~taxonomy_df["pred_genome_struc"].isin(pred_genome_struc_allowed)
        ]
        if not invalid.empty:
            invalid_vals = ", ".join(map(str, invalid["pred_genome_struc"].unique()))
            raise click.ClickException(
                f"Invalid value(s) in column 'pred_genome_struc': {invalid_vals}. Allowed values: {', '.join(pred_genome_struc_allowed)}."
            )

    # 3. Read the features and miuvig files (key/value format) into dictionaries.
    features_dict = (
        pd.read_csv(features, sep="\t").set_index("MIUVIG_parameter")["value"].to_dict()
    )
    miuvig_dict = (
        pd.read_csv(miuvig, sep="\t").set_index("MIUVIG_parameter")["value"].to_dict()
    )

    # 4. Merge the dictionaries (miuvig values take precedence).
    structured_comment_dict = {
        "StructuredCommentPrefix": "MIUVIG:5.0-Data",
        "StructuredCommentSuffix": "MIUVIG:5.0-Data",
    }

    merged_params = {**features_dict, **miuvig_dict, **structured_comment_dict}

    # 5. Early check on merged parameters:
    # 5a. Check formatting for software columns.
    for key in ["assembly_software", "vir_ident_software"]:
        if key in merged_params:
            value = merged_params[key]
            if not isinstance(value, str):
                raise click.ClickException(
                    f"Value for {key} must be a string in the format 'software;version;parameters'. Got: {value}"
                )
            if value.count(";") != 2:
                raise click.ClickException(
                    f"Invalid format for {key}: {value}. Expected format: 'software;version;parameters'."
                )

    # 5b. For any merged parameter that should have a restricted set of values,
    # check its value against the allowed list.
    for key, allowed in allowed_values.items():
        if key in merged_params:
            value = merged_params[key]
            if key == "virus_enrich_appr":
                vea = list(map(str.strip, value.split("+")))
                invalid_values = [
                    v for v in vea if v not in allowed
                ]  # Collect invalid values
                if invalid_values:  # If there's any invalid value, raise an error
                    raise click.ClickException(
                        f"Invalid value(s) for {key}: {', '.join(invalid_values)}.\n"
                        f"Allowed values: {', '.join(allowed)}.\n"
                        f"Allowed values should be separated by a '+'."
                    )

                # Update merged_params with cleaned value
                merged_params[key] = " + ".join(vea)
            else:
                if value not in allowed:
                    raise click.ClickException(
                        f"Invalid value for {key}: {value}.\nAllowed values: {', '.join(allowed)}."
                    )

    # 6. Add merged parameters as new constant columns to the taxonomy DataFrame.
    for param, val in merged_params.items():
        taxonomy_df[param] = val

    # 7. Reorder columns.
    desired_order = [
        "contig",
        "source_uvig",
        "assembly_software",
        "vir_ident_software",
        "pred_genome_type",
        "pred_genome_struc",
        "detec_type",
        "assembly_qual",
        "number_contig",
        "feat_pred",
        "ref_db",
        "sim_search_method",
        "size_frac",
        "virus_enrich_appr",
        "nucl_acid_ext",
        "wga_amp_appr",
    ]
    desired_existing = [col for col in desired_order if col in taxonomy_df.columns]
    remaining_cols = [col for col in taxonomy_df.columns if col not in desired_existing]
    taxonomy_df = taxonomy_df[desired_existing + remaining_cols]
    taxonomy_df.rename(columns={"contig": "SeqID"}, inplace=True)

    # 8. Ensure the output directory exists, but only if a directory is specified
    output_dir = os.path.dirname(output)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    ## 9. Write the combined DataFrame to a TSV file.
    # taxonomy_df.to_csv(os.path.join(output, ".cmt"), sep="\t", index=False)
    # click.echo(f"Combined file written to {output}")

    # 9. Write the combined DataFrame to a plain text file with actual tab characters
    with open(output, "w") as file:
        file.write("\\t".join(taxonomy_df.columns) + "\n")  # Write the header
        for _, row in taxonomy_df.iterrows():
            file.write(
                "\\t".join(map(str, row)) + "\n"
            )  # Write each row with tab-separated values

    click.echo(f"Combined file written to {output}.cmt")


if __name__ == "__main__":
    comments()
