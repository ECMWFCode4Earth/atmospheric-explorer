# Atmospheric Composition Dataset Explorer
This repository contains an interactive application as well as APIs to generate some atmospheric composition
diagnostics plots with CAMS datasets. The datasets currently supported are
* [CAMS greenhouse gas fluxes](https://ads.atmosphere.copernicus.eu/cdsapp#!/dataset/cams-global-greenhouse-gas-inversion?tab=overview)
* [CAMS reanalysis (EAC4)](https://ads.atmosphere.copernicus.eu/cdsapp#!/dataset/cams-global-reanalysis-eac4?tab=overview)

This project has been developed during [Code for Earth](https://codeforearth.ecmwf.int/) 2023, an initiative by ECMWF.

## Example plots
*!! Add plot screenshots (same as in challenge description) and explain them briefly from a scientific point of view*

# How to use it

## How to install the package
*!! TODO*

## Interactive Streamlit application
To run the streamlit application, install the package with

```pip install -e .```

and run in the terminal the command

```atmospheric-explorer```

*!! Add example gif*

## CLI
*!! TODO. Example gif here as well?*

## APIs
The high-level files containing functions to access the plotting APIs are in `./atmospheric_explorer/api/plotting`.
You can also use util functions contained in the `data_interface` and `shape_selection` directories.

# How to contribute
See the **APIs** section above for a quick summary about the API functions that you might want to edit and expand.

## Pre-commit
This repo uses `pre-commit` to run a number of checks before committing (formatting, linting, tests ecc.). In order to enable `pre-commit`:
- In a terminal, create an python env using the command `conda env create -f env.yml`
- Activate the environment with `conda activate atmospheric-explorer`
- Run `pre-commit install`
- Now the checks will run when trying to commit, if any check fails the changes won't be committed
- To see the output of all checks before committing, you can run `pre-commit` in a terminal

Once pre-commit is enabled, it will run a number of check on **staged files**. All checks should pass before the changes can be commited.

## Logger
The logger configuration is defined in `logger.py` inside a dictionary.

At the moment we only have one logger called `main`, if you want to use it just import it as show below
```
from .loggers import get_logger
logger = get_logger("main")
```
