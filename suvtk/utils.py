"""
utils.py
========

This script provides utility functions for executing shell commands, reading CSV files safely,
and determining the number of available CPUs. These utilities are used across various modules
in the project.

Functions
---------
Exec(CmdLine, fLog=None, capture=False)
    Execute a shell command and optionally log or capture the output.

safe_read_csv(path, **kwargs)
    Read a CSV file with ASCII encoding and handle UnicodeDecodeError.

get_available_cpus()
    Get the number of available CPUs for the current process.
"""

import os
import subprocess
import sys

import pandas as pd
import rich_click as click


# Adapted from https://github.com/rcedgar/palm_annot/blob/77ac88ef7454dd3be9e5cbdb55792ce1ed7db95c/py/palm_annot.py#L121-L132
def Exec(CmdLine, fLog=None, capture=False, raise_on_error=True):
    """
    Execute a shell command with optional logging and output capture.

    Parameters
    ----------
    CmdLine : str
        The command line string to execute in the shell.
    fLog : file-like object, optional
        A file object (opened for writing) to which stdout and stderr
        will be written. If `None`, no file logging is performed.
    capture : bool, default=False
        If True, captures stdout and stderr and returns stdout upon success.
        If False, outputs are printed directly to the console.
    raise_on_error : bool, default=True
        If True, raises a `subprocess.CalledProcessError` when the command
        exits with a non-zero return code. If False, returns a dictionary
        containing the command results instead.

    Returns
    -------
    str or None or dict
        - If `capture` is True and the command succeeds, returns the captured
          stdout as a string.
        - If `capture` is False and the command succeeds, returns None.
        - If `raise_on_error` is False and the command fails, returns a dict
          with keys:
            - 'returncode' : int
                Exit status of the process.
            - 'stdout' : str or None
                Captured standard output, if any.
            - 'stderr' : str or None
                Captured standard error, if any.
            - 'cmd' : str
                The command that was executed.

    Raises
    ------
    subprocess.CalledProcessError
        If the command returns a non-zero exit code and `raise_on_error`
        is True. The exception includes the return code, command, stdout,
        and stderr.

    Notes
    -----
    - When `capture` is False, stdout and stderr are streamed directly to
      the console instead of being captured.
    - Both stdout and stderr are written to `fLog` if provided, regardless
      of the `capture` setting.
    """

    def write_log(message, is_error=False):
        # Always write to fLog if provided
        if fLog and message:
            fLog.write(message)

        # Print to console only when not capturing
        if not capture and message:
            stream = sys.stderr if is_error else sys.stdout
            stream.write(message)

    # Set up pipes explicitly to control capture behavior
    stdout_pipe = subprocess.PIPE if capture else None
    stderr_pipe = subprocess.PIPE if capture else None

    result = subprocess.run(
        CmdLine,
        shell=True,
        stdout=stdout_pipe,
        stderr=stderr_pipe,
        text=True,
        check=False,
    )

    # Log outputs if we have them
    if result.stdout:
        write_log(result.stdout)
    if result.stderr:
        write_log(result.stderr, is_error=True)

    if result.returncode == 0:
        return result.stdout if capture else None

    # Handle non-zero exit
    if raise_on_error:
        # Preserve legacy behavior: raise with captured data if available
        raise subprocess.CalledProcessError(
            result.returncode, CmdLine, output=result.stdout, stderr=result.stderr
        )

    # Caller can inspect this without exceptions
    return {
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "cmd": CmdLine,
    }


def safe_read_csv(path, **kwargs):
    """
    Reads a CSV file using ASCII encoding. If a UnicodeDecodeError occurs,
    raises a ClickException showing the offending character.

    Parameters
    ----------
    path : str
        Path to the CSV file.
    **kwargs : dict
        Additional arguments to pass to `pandas.read_csv`.

    Returns
    -------
    pandas.DataFrame
        The contents of the CSV file.

    Raises
    ------
    click.ClickException
        If the file contains non-ASCII characters.
    """
    try:
        return pd.read_csv(path, encoding="ascii", **kwargs)
    except UnicodeDecodeError as e:
        offending_bytes = e.object[e.start : e.end]
        # Try decoding using UTF-8 to show the offending character
        try:
            offending_char = offending_bytes.decode("utf-8")
        except Exception:
            offending_char = repr(offending_bytes)
        raise click.ClickException(
            f"Only ASCII characters are allowed in file '{path}'. "
            f"Offending character: {offending_char}. Error: {str(e)}"
        )


# Copied from https://github.com/EricDeveaud/genomad/blob/030ab6434654435ce75243347c97be6f40ea175b/genomad/cli.py#L250-L257
def get_available_cpus():
    """
    Get the number of available CPUs for the current process.

    Returns
    -------
    int
        The number of available CPUs.
    """
    try:
        # Try to get the number of cores available to this process
        CPUS = len(os.sched_getaffinity(0))
    except AttributeError:
        # Windows / MacOS probably don't have this functionality
        CPUS = os.cpu_count()
    return CPUS
