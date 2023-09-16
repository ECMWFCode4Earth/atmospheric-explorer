# Atmospheric Composition Dataset Explorer
This repository contains an interactive application as well as APIs to generate some atmospheric composition
diagnostics plots with CAMS datasets. The datasets currently supported are
* [CAMS greenhouse gas fluxes](https://ads.atmosphere.copernicus.eu/cdsapp#!/dataset/cams-global-greenhouse-gas-inversion?tab=overview)
* [CAMS reanalysis (EAC4)](https://ads.atmosphere.copernicus.eu/cdsapp#!/dataset/cams-global-reanalysis-eac4?tab=overview)

This project has been developed during [Code for Earth](https://codeforearth.ecmwf.int/) 2023, an initiative by ECMWF. [Here](https://github.com/ECMWFCode4Earth/challenges_2023/issues/2) is the original challenge description.

<!--- TODO: ## Example plots
Add plot screenshots (same as in challenge description) and explain them briefly from a scientific point of view -->

# How to use it

## How to install the package
First of all, you must install the `atmospheric-explorer` Python package. Follow these steps:
1. Create a Conda virtual environment with all required packages running this command in your terminal (from the project root directory):

    ```conda env create -f env.yml```

2. Activate the virtual environment:

    ```conda activate atmospheric-explorer```

3. Install the `atmospheric-explorer` package with

    ```pip install .```

4. You can now run the interactive Streamlit application or the CLI tool.

## Interactive Streamlit application
To run the Streamlit application, after following the steps above, run this command in the terminal:

```atmospheric-explorer run```

<!--- TODO: Add example gif -->

## CLI
<!--- TODO. Example gif here as well? -->

You can also create and save plots from the terminal via command-line interface (CLI). Through this tool, you can also access util functionalities to manage the app's downloaded data and logs.

After installing the package and activating the virtual environment, as described in the first section, you can simply use it by running `atmospheric-explorer` in the terminal.

A list and description of the commands can be accessed from the terminal by running

```atmospheric-explorer --help```

## APIs
The high-level files containing functions to access the plotting APIs are in `atmospheric_explorer/api/plotting`.
You can also use util functions contained in the `data_interface` and `shape_selection` directories.

<!--- TODO: add quickstart about how to use the APIs -> function call to create a plot from the start, i.e. package installation, to the end. Add this static page on Sphinx, and also a similar one about the CLI. -->

# How to contribute
See the **APIs** section above for a quick summary about the API functions that you might want to edit and expand.

If you also want to contribute to the project besides using it as a user, you must also install `dev-requirements` running this command (after having activated the `atmospheric-explorer` virtual environment):

```pip install -r dev-requirements.txt```

When you add any new code to the APIs, you will probably also want to include it in the **CLI** and **UI** in their respective folders.

<!--- TODO: write something more about contributing to CLI and UI (how to add functionalities using Click and Streamlit) -->

To contribute best, you should also follow the practices described below.

## Pre-commit
This repo uses `pre-commit` to run a number of checks before committing (formatting, linting, tests etc).

In order to enable `pre-commit`, after activating the `atmospheric-explorer` virtual environment, run this command:

```pre-commit install```

Now the checks will run when trying to commit: if any check fails, the changes won't be committed. To see the output of all checks before committing, you can run `pre-commit` in a terminal.

Once pre-commit is enabled, it will run a number of check on **staged files**. All checks should pass before the changes can be commited.

## Logger
The logger configuration is defined in `logger.py` inside a dictionary.

At the moment we only have one logger called `main`, if you want to use it just import it as show below
```
from .loggers import get_logger
logger = get_logger("main")
```

## Sphinx documentation
To update the documentation, you must run the following commands.

1. To re-generate the APIs documentation source `rst` files based on docstrings:

    ```sphinx-apidoc -f -o documentation\source\ atmospheric_explorer\api\```

    The first path is where the documentation will be created.

2. To build the `html` files with the documentation, from inside the `documentation` folder:

    ```make html```

## Unit tests
Most API functionalities are tested using `pytest` inside the `tests` folder.
