import click
import gbk2tbl


@click.group()
@click.version_option()
def cli():
    "Tool to submit viral sequences to Genbank."


@cli.command(name="command")
@click.argument(
    "example"
)
@click.option(
    "-o",
    "--option",
    help="An example option",
)
def first_command(example, option):
    "Command description goes here"
    click.echo("Here is some output")
