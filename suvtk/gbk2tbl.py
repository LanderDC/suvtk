# adapted from https://github.com/wanyuac/BINF_toolkit/blob/master/gbk2tbl.py
# TODO: generally improve script
# TODO: add option to keep locus_tag as allowed qualifier + fix spaces breaking up names because they are too long
r"""
This script converts a GenBank file (.gbk or .gb) into a Sequin feature table (.tbl), which is an input file of table2asn used for creating an ASN.1 file (.sqn).

Package requirement: BioPython and click

Examples
--------
Simple command:
    python gbk2tbl.py --mincontigsize 200 --prefix any_prefix --input annotation.gbk


Inputs
------
GenBank file
    Passed to the script through input.

Outputs
-------
any_prefix.tbl : str
    The Sequin feature table.
any_prefix.fsa : str
    The corresponding FASTA file.

Arguments
---------
--mincontigsize : int, optional
    The minimum contig size, default = 0.
--prefix : str, optional
    The prefix of output filenames, default = 'seq'.

Notes
-----
    These files are inputs for table2asn which generates ASN.1 files (*.sqn).

Development notes
-----------------
    This script is derived from the one developed by SEQanswers users nickloman (https://gist.github.com/nickloman/2660685/genbank_to_tbl.py) and ErinL who modified nickloman's script and put it on the forum post (http://seqanswers.com/forums/showthread.php?t=19975).

    Author of this version: Yu Wan (wanyuac@gmail.com, github.com/wanyuac)
    Creation: 20 June 2015 - 11 July 2015; the latest edition: 21 October 2019

    Dependency: Python versions 2 and 3 compatible.

    Licence: GNU GPL 2.1
"""

from __future__ import print_function

import sys

import click
from Bio import SeqIO


@click.command(short_help="Convert a GenBank flatfile into a feature table (.tbl).")
@click.option(
    "-i",
    "--input",
    type=click.Path(exists=True),
    required=True,
    help="Input genbank file",
)
@click.option(
    "-m",
    "--mincontigsize",
    type=int,
    required=False,
    default=0,
    help="The minimum contig length",
)
@click.option(
    "-p",
    "--prefix",
    type=str,
    required=False,
    default="seq",
    help="The prefix of output filenames",
)
def gbk2tbl(input, mincontigsize, prefix):
    """
    This script converts a GenBank file (.gbk or .gb) into a Sequin feature table (.tbl), which is an input file of table2asn used for creating an ASN.1 file (.sqn).
    """
    allowed_qualifiers = [
        "gene",
        "product",
        "function",
        "pseudo",
        "protein_id",
        "gene_desc",
        "note",
        "inference",
        "organism",
        "mol_type",
        "strain",
        "sub_species",
        "isolation_source",
        "country",
        "collection_date",
        "transl_table",
        "codon_start",
        "source",
        "anticodon",
        "rpt_type",
        "rpt_family",
        "rpt_unit_seq",
        "rpt_unit_range",
    ]
    """
	These are selected qualifiers because we do not want to see qualifiers such as 'translation' or 'codon_start' in the feature table.
	Qualifiers 'organism', 'mol_type', 'strain', 'sub_species', 'isolation-source', 'country' belong to the feature 'source'.
	"""

    contig_num = 0
    fasta_fh = open(prefix + ".fsa", "w")  # the file handle for the fasta file
    feature_fh = open(prefix + ".tbl", "w")  # the file handle for the feature table
    records = list(
        SeqIO.parse(input, "genbank")
    )  # read a GenBank file from the standard input and convert it into a list of SeqRecord objects

    for rec in records:  # for every SeqRecord object in the list 'records'
        if len(rec) <= mincontigsize:  # filter out small contigs
            print("skipping small contig %s" % (rec.id), file=sys.stderr)
            continue  # start a new 'for' loop
        contig_num += 1
        print(rec.name)  # print the contig name to STDOUT

        # write the fasta file
        SeqIO.write(
            [rec], fasta_fh, "fasta"
        )  # Prints this contig's sequence to the fasta file. The sequence header will be rec.description.

        # write the feature table
        print(
            ">Feature %s" % (rec.name), file=feature_fh
        )  # write the first line of this record in the feature table: the LOCUS name
        for f in rec.features:
            # print the coordinates
            if f.location.strand == 1:
                print(
                    "%d\t%d\t%s" % (f.location.start + 1, f.location.end, f.type),
                    file=feature_fh,
                )
            else:
                print(
                    "%d\t%d\t%s" % (f.location.end, f.location.start + 1, f.type),
                    file=feature_fh,
                )

            if (f.type == "CDS") and ("product" not in f.qualifiers):
                f.qualifiers["product"] = "hypothetical protein"

            # print qualifiers (keys and values)
            for key, values in f.qualifiers.items():
                """
                Apply the iteritems() method of the dictionary f.qualifiers for (key, values) pairs
                iteritems() is a generator that yields 2-tuples for a dictionary. It saves time and memory but is slower than the items() method.
                """
                if key not in allowed_qualifiers:
                    continue  # start a new 'for' loop of f, skipping the following 'for' statement of v
                for (
                    v
                ) in values:  # else, write all values under this key (qualifier's name)
                    print("\t\t\t%s\t%s" % (key, v), file=feature_fh)
    fasta_fh.close()  # finish the generation of the FASTA file
    feature_fh.close()  # finish the generation of the feature table
    print(str(contig_num) + " records have been converted.")


# call the main function
if __name__ == "__main__":
    gbk2tbl()
