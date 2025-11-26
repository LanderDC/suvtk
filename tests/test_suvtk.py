"""
Tests for command line interface (CLI).
"""

import shutil
from importlib import import_module
from importlib.metadata import version
from os import linesep

from cli_test_helpers import shell
from click.exceptions import UsageError
from click.testing import CliRunner

from suvtk.cli import cli


def test_main_module():
    """
    Exercise (most of) the code in the ``__main__`` module.
    """
    import_module("suvtk.__main__")


def test_runas_module():
    """
    Can this package be run as a Python module?
    """
    result = shell("python -m suvtk --help")
    assert result.exit_code == 0


def test_entrypoint():
    """
    Is entrypoint script installed? (pyproject.toml)
    """
    assert shutil.which("suvtk")


def test_usage():
    """
    Does CLI abort w/o arguments, displaying usage instructions?
    """
    runner = CliRunner()
    result = runner.invoke(cli)

    assert "Usage:" in result.output
    assert result.exit_code == UsageError.exit_code


def test_version():
    """
    Does --version display information as expected?
    """
    expected_version = version("suvtk")
    result = shell("suvtk --version")

    assert result.stdout == f"suvtk {expected_version}{linesep}"
    assert result.exit_code == 0


def test_database_command():
    """
    Is database command available?
    """
    result = shell("suvtk download-database --help")
    assert result.exit_code == 0


def test_taxonomy_command():
    """
    Is taxonomy command available?
    """
    result = shell("suvtk taxonomy --help")
    assert result.exit_code == 0


def test_features_command():
    """
    Is features command available?
    """
    result = shell("suvtk features --help")
    assert result.exit_code == 0


def test_virus_info_command():
    """
    Is virus-info command available?
    """
    result = shell("suvtk virus-info --help")
    assert result.exit_code == 0


def test_co_occurrence_command():
    """
    Is co-occurrence command available?
    """
    result = shell("suvtk co-occurrence --help")
    assert result.exit_code == 0


def test_gbk2tbl_command():
    """
    Is gbk2tbl command available?
    """
    result = shell("suvtk gbk2tbl --help")
    assert result.exit_code == 0


def test_comments_command():
    """
    Is comments command available?
    """
    result = shell("suvtk comments --help")
    assert result.exit_code == 0


def test_table2asn_command():
    """
    Is table2asn command available?
    """
    result = shell("suvtk table2asn --help")
    assert result.exit_code == 0
