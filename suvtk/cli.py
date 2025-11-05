"""
cli.py
=======

This script provides a command-line interface (CLI) for submitting viral sequences to GenBank.
It includes various subcommands for processing and preparing data, such as taxonomy assignment,
feature extraction, structured comment generation, and more.

Classes
-------
FullHelpGroup
    Custom Click Group to display commands in the order they were added.

Functions
---------
cli()
    Main entry point for the CLI tool.

Commands
--------
- download-database
- taxonomy
- features
- virus_info
- co_occurrence
- gbk2tbl
- comments
- table2asn
"""

from gettext import gettext as _

import rich_click as click

from suvtk import (
    co_occurrence,
    comments,
    download_database,
    features,
    gbk2tbl,
    table2asn,
    taxonomy,
    virus_info,
)


class FullHelpGroup(click.RichGroup):
    """
    Custom Click Group to display commands in the order they were added.

    Methods
    -------
    list_commands(ctx: click.Context)
        Return commands in the order they were added.
    format_commands(ctx: click.Context, formatter: click.HelpFormatter)
        Formats and displays commands in the correct order.
    """

    def list_commands(self, ctx: click.RichContext):
        """
        Return commands in the order they were added.

        Parameters
        ----------
        ctx : click.Context
            The Click context.

        Returns
        -------
        list
            List of command names in the order they were added.
        """
        return list(self.commands.keys())

    def format_commands(self, ctx: click.RichContext, formatter: click.HelpFormatter):
        """
        Delegate formatting to the parent implementation so rich-click can
        apply its rich formatting. We keep the custom ordering by overriding
        list_commands only.
        """
        return super().format_commands(ctx, formatter)


CONTEXT_SETTINGS = dict(
    help_option_names=["-h", "--help"], show_default=True, max_content_width=120
)


@click.group(context_settings=CONTEXT_SETTINGS, cls=FullHelpGroup)
@click.version_option(None, "-v", "--version", message="%(prog)s %(version)s")
def cli():
    """
    The suvtk CLI tool provides various commands to process and submit viral
    sequences to Genbank.
    """


cli.add_command(download_database)
cli.add_command(taxonomy)
cli.add_command(features)
cli.add_command(virus_info)
cli.add_command(co_occurrence)
cli.add_command(gbk2tbl)
cli.add_command(comments)
cli.add_command(table2asn)


if __name__ == "__main__":
    cli()
