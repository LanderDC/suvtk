"""
download_database.py
====================

This script downloads and extracts the suvtk database as a gzipped tar file from Zenodo.

Functions
---------
doi_to_record_id(doi: str) -> str
    Extract the numeric record ID from a Zenodo DOI.

fetch_record_metadata(record_id: str) -> dict
    Fetch the Zenodo record metadata in JSON form.

find_tar_file(files: list) -> dict
    Locate the first `.tar` or `.tar.gz` file in the record's files list.

download_file(url: str, dest: str, chunk_size: int = 1024 * 1024)
    Stream-download a file from a URL to a local path.

unpack_tar(archive: str, output_dir: str = None)
    Extract a `.tar` or `.tar.gz` archive to a directory.

"""

import os
import tarfile

import requests
import rich_click as click

# The Zenodo DOI is fixed
ZENODO_DOI = "10.5281/zenodo.15374439"


def doi_to_record_id(doi: str) -> str:
    """
    Extract the numeric record ID from a Zenodo DOI.
    """
    try:
        return doi.strip().split(".")[-1]
    except IndexError:
        raise RuntimeError(f"Invalid DOI format: {doi}")


def fetch_record_metadata(record_id: str) -> dict:
    """
    Fetch the Zenodo record metadata in JSON form.
    """
    api_url = f"https://zenodo.org/api/records/{record_id}"
    response = requests.get(api_url)
    response.raise_for_status()
    return response.json()


def find_tar_file(files: list) -> dict:
    """
    From the record's files list, locate the first .tar or .tar.gz.
    """
    for f in files:
        key = f.get("key", "")
        if key.endswith((".tar", ".tar.gz")):
            return f
    raise RuntimeError("No .tar or .tar.gz file found in this record.")


def download_file(url: str, dest: str, chunk_size: int = 1024 * 1024):
    """
    Stream-download a file from `url` to local path `dest`.
    """
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        total = int(r.headers.get("content-length", 0))
        click.echo(f"Downloading {url} → {dest}")
        downloaded = 0
        with open(dest, "wb") as fd:
            for chunk in r.iter_content(chunk_size=chunk_size):
                if chunk:
                    fd.write(chunk)
                    downloaded += len(chunk)
                    if total:
                        click.echo(
                            f"  {downloaded/1e6:.1f} MB / {total/1e6:.1f} MB", nl=False
                        )
                        click.echo("\r", nl=False)
        click.echo("\nDownload complete.")


def unpack_tar(archive: str, output_dir: str = None):
    """
    Extract a .tar or .tar.gz archive into the specified output_dir
    (defaults to current directory), preserving all folder structure.
    """
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    else:
        output_dir = os.getcwd()

    click.echo(f"Extracting {archive} into {output_dir}")
    with tarfile.open(archive, "r:*") as tar:
        tar.extractall(path=output_dir)
    click.echo("Extraction complete.")


@click.command(short_help="Download and extract the suvtk database archive.")
@click.option(
    "--output-dir",
    "-o",
    type=click.Path(),
    default=None,
    help="Directory to extract the archive into (defaults to archive name)",
)
def download_database(output_dir):
    """
    Download and extract the TAR archive from the fixed Zenodo DOI.
    """
    record_id = doi_to_record_id(ZENODO_DOI)
    metadata = fetch_record_metadata(record_id)
    tar_info = find_tar_file(metadata.get("files", []))

    # Zenodo file entries expose download links under 'links'.
    links = tar_info.get("links", {})
    download_url = links.get("download") or links.get("self")
    if not download_url:
        raise RuntimeError(
            f"No downloadable link found for file '{tar_info.get('key')}'."
        )

    filename = tar_info["key"]

    download_file(download_url, filename)
    unpack_tar(filename, output_dir)


if __name__ == "__main__":
    download_database()
