# suvtk (Submission of Uncultivated Viral genomes toolkit)

[![Changelog](https://img.shields.io/github/v/release/LanderDC/suvtk?include_prereleases&label=release&color=purple&logo=github)](https://github.com/LanderDC/suvtk/releases)
[![PyPI](https://img.shields.io/pypi/v/suvtk.svg?color=blue&logo=python)](https://pypi.org/project/suvtk/)
[![Bioconda](https://img.shields.io/conda/v/bioconda/suvtk?label=bioconda&labelColor=grey&color=brightgreen&logo=anaconda)](https://bioconda.github.io/recipes/suvtk/README.html)
[![Tests](https://github.com/LanderDC/suvtk/actions/workflows/test.yml/badge.svg)](https://github.com/LanderDC/suvtk/actions/workflows/test.yml)
[![License](https://img.shields.io/github/license/LanderDC/suvtk?color=blue)](https://github.com/LanderDC/suvtk/blob/master/LICENSE)

> [!WARNING]
>    `suvtk` is still under active development. If you encounter any problems, please let me know by creating an [issue](https://github.com/LanderDC/suvtk/issues).

Tool to submit viral sequences to Genbank.

## Documentation

Documentation for the tool (including installation instruction) is available <a href="https://landerdc.github.io/suvtk/" target="_blank">here</a>.

## Usage

For help, run:
```bash
suvtk --help
```
You can also use:
```bash
python -m suvtk --help
```
## Development

To contribute to this tool, first checkout the code. Then create a new virtual environment:
```bash
cd suvtk
python -m venv venv
source venv/bin/activate
```
Now install the dependencies and test dependencies:
```bash
pip install -e '.[test]'
```
To run the tests:
```bash
python -m pytest
```
