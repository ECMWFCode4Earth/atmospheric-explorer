# Atmospheric Composition Dataset Explorer

This repository contains an interactive application as well as APIs to generate some atmospheric composition
diagnostics plots with CAMS datasets. The datasets currently supported are
* [CAMS greenhouse gas fluxes](https://ads.atmosphere.copernicus.eu/cdsapp#!/dataset/cams-global-greenhouse-gas-inversion?tab=overview)
* [CAMS reanalysis (EAC4)](https://ads.atmosphere.copernicus.eu/cdsapp#!/dataset/cams-global-reanalysis-eac4?tab=overview)

This project has been developed during [Code for Earth](https://codeforearth.ecmwf.int/) 2023, an initiative by ECMWF. [Here](https://github.com/ECMWFCode4Earth/challenges_2023/issues/2) is the original challenge description.

<!--- TODO: ## Example plots
Add plot screenshots (same as in challenge description) and explain them briefly from a scientific point of view -->

# How to use it

This application offers three ways to access its functionalities:

- Low level APIs
- Command-line interface (CLI), which offers a subset of functionalities for quickly generating plots and managing the downloaded data and logs
- Streamlit UI, which offers the same functionality as the CLI for generating plots, most useful when exploring the data

## How to install the package

First of all, you must install the `atmospheric-explorer` Python package. We recommend to install the package in a dedicated virtual environment. Here we describe how to do so using Conda, but you can use any tool to create a virtual environment:

1. Move to the project root folder, i.e. the folder with the `pyproject.toml` and `env.yml` files

2. Create a Conda virtual environment with all required packages running this command in your terminal (from the project root directory):

    ```bash
    $ conda env create -f env.yml
    ```

2. Activate the virtual environment:

    ```bash
    $ conda activate atmospheric-explorer
    ```

3. Install the `atmospheric-explorer` package with

    ```bash
    $ pip install -e .
    ```

4. You can now use the APIs, run the CLI tool or the interactive Streamlit application.

## Interactive Streamlit application

The APIs come with a frontend built using [Streamlit](https://streamlit.io/). To run the Streamlit UI, install the package as described in the previous section and then run this command in the terminal:

```bash
atmospheric-explorer run
```

## CLI

You can also create and save plots from the terminal via command-line interface (CLI). Through this tool, you can also access utility functionalities to manage the app's downloaded data and logs.

After installing the package and activating the virtual environment, as described in the first section, you can access the CLI with the command `atmospheric-explorer`.

A list and description of the commands can be accessed from the terminal by running

```bash
$ atmospheric-explorer --help
```

As an example, let's generate an anomalies plot. First, let's run

```bash
$ atmospheric-explorer --help

Usage: atmospheric-explorer [OPTIONS] COMMAND [ARGS]...

  Command-line interface for Atmospheric Composition Dataset Explorer.

Options:
  --help  Show this message and exit.

Commands:
  data  Command to interact with downloaded data
  logs  Command to interact with logs
  plot  Plotting CLI
  run   Run this app
```

We can see that the `atmospheric-explorer` command accepts four sub-commands `data`, `logs`, `plot` and `run`. We alredy met `run` in the previous section, it start the UI. Here we are interested in `plot`:

```bash
$ atmospheric-explorer plot --help

Usage: atmospheric-explorer plot [OPTIONS] COMMAND [ARGS]...

  Plotting CLI

Options:
  --help  Show this message and exit.

Commands:
  anomalies    CLI command to generate anomalies plot.
  hovmoeller   CLI command to generate hovmoeller plot.
  yearly-flux  CLI command to generate yearly flux plot.
```

In the help we see that plot accepts three subcommand. Let's try `anomalies`:

```bash
$ atmospheric-explorer plot anomalies --help

Usage: atmospheric-explorer plot anomalies [OPTIONS]

  CLI command to generate anomalies plot.

Options:
  -v, --data-variable TEXT        Data variable  [required]
  -r, --dates-range TEXT          Start/End dates of range, using format YYYY-
                                  MM-DD  [required]
  -t, --time-values [00:00|03:00|06:00|09:00|12:00|15:00|18:00|21:00]
                                  Time value. Multiple values can be chosen
                                  calling this option multiple times, e.g. -t
                                  00:00 -t 03:00.       [required]
  --title TEXT                    Plot title  [required]
  --output-file TEXT              Absolute path of the resulting image
                                  [required]
  --reference-range TEXT          Start/End dates of reference range, using
                                  format YYYY-MM-DD
  --entities TEXT                 Comma separated list of entities to select,
                                  e.g. Italy,Spain,Germany or Europe,Africa
  --selection-level [Generic|Continents|Organizations|Countries|Sub-national divisions]
                                  Selection level. Mandatory if --entities is
                                  specified, must match entities level.

                                  e.g. --entities Europe,Africa --selection-
                                  level Continents
  --resampling [1MS|YS]           Month/year resampling
  --width INTEGER                 Image width
  --height INTEGER                Image height
  --scale FLOAT                   Image scale. A number larger than 1 will
                                  upscale the image resolution.
  --help                          Show this message and exit.
```

As you can see, once we get to the last command, i.e. the one that actually generates the plot, all options are described. For some options, all possible values are listed directly in the CLI help.
Let's generate an anomalies plot for the Total column ozone over Italy, Germany and Spain for the date range `2021-01-01/2021-06-01` and time set at midnight and at 3 a.m.

```bash
$ atmospheric-explorer plot anomalies --data-variable total_column_ozone --dates-range 2021-01-01/2021-06-01 -t 00:00 -t 03:00 --title 'Total column ozone' --output-file plot.png --entities Italy,Germany,Spain --selection-level Countries
```

This command will download the necessary data, generate the plot and save it as an image with the name specified in the _required_ option `--output-file`.

The values accepted by `--data-variables` are the same as the `variable` parameter accepted by [`cdsapi`](https://cds.climate.copernicus.eu/api-how-to). If you're unsure which value to pass, you can:

- Use the UI, which presents a mapping of all possible variables to choose from
- Use the API as shown in the next section
- Refer to the [CAMS ADS datasets page](https://ads.atmosphere.copernicus.eu/cdsapp#!/search?type=dataset) for reference

## APIs
The APIs source files are in `atmospheric_explorer/api`.
This section will briefly go over some main concepts, for more in depth use we refer the reader to the API documentation.

### Datasets

Let's see how to interact with the provided datasets: EAC4 and global inversion. The functionalities to manage and download the data of these dataset can be found in

```python
import atmospheric_explorer.api.data_interface.eac4 # EAC4 dataset
import atmospheric_explorer.api.data_interface.ghg # Global inversion dataset
```

First of all, in the previous section, we mentioned a mapping of all possible `--data-variables`: there's a mapping for each dataset in a dedicated `YAML` file, e.g. for the EAC4 dataset it can be found in the `atmospheric_explorer/api/data_interface/eac4/eac4_config.yaml` file. These mappings can also be accessed through the API:

```python
from atmospheric_explorer.api.data_interface.eac4 import EAC4Config

EAC4Config.get_config()['variables']

{'10m_u_component_of_wind': {'conversion': {'conversion_factor': 1,
   'convert_unit': 'm s**-1'},
  'var_name': 'u10',
  'var_type': 'single_level',
  'short_name': 'u10',
  'long_name': '10 metre U wind component'},
...
```

All variables are in the `variables` section of the file. For each dataset you also have some further variables, e.g. all Pressure levels for the EAC4 dataset

```python
from atmospheric_explorer.api.data_interface.eac4 import EAC4Config

EAC4Config.get_config()['pressure_levels']

[1, 2, 3, 5, 7, 10, 20, 30, 50, 70, 100, 150, 200, 250, 300, 400, 500, 600, 700, 800, 850, 900, 925, 950, 1000]
```

Let's now see how to download the data. We will work with the EAC4 but the same can be done for the global inversion dataset.

```python
from atmospheric_explorer.api.data_interface.eac4 import EAC4Instance

eac4 = EAC4Instance(
    data_variables=["total_column_ozone", "total_column_methane"],
    dates_range="2021-01-01/2021-04-01",
    time_values=["00:00", "03:00"]
)
```

Notice that here we didn't download the data, but just instantiated an `EAC4Instance` object which represents the data. To download the data, use the `.download()` command

```python
eac4.download()

2023-09-19 23:58:18,004 INFO Created folder /home/luigi/.atmospheric_explorer/data
2023-09-19 23:58:18,004 INFO Created folder /home/luigi/.atmospheric_explorer/data/cams-global-reanalysis-eac4/data_3
2023-09-19 23:58:18,192 INFO Welcome to the CDS
2023-09-19 23:58:18,195 INFO Sending request to https://ads.atmosphere.copernicus.eu/api/v2/resources/cams-global-reanalysis-eac4
2023-09-19 23:58:18,249 INFO Request is queued
2023-09-19 23:58:19,299 INFO Request is running
2023-09-19 23:58:39,886 INFO Request is completed
2023-09-19 23:58:39,888 INFO Downloading https://download-0002-ads-clone.copernicus-climate.eu/cache-compute-0002/cache/data4/adaptor.mars.internal-1695160711.7235253-3119-8-c1f3df7f-169f-4c62-b66e-2942e4175aef.nc to /home/luigi/.atmospheric_explorer/data/cams-global-reanalysis-eac4/data_3/data_3.nc (80.3M)
2023-09-19 23:59:32,879 INFO Download rate 1.5M/s
2023-09-19 23:59:32,937 INFO Finished downloading file /home/luigi/.atmospheric_explorer/data/cams-global-reanalysis-eac4/data_3/data_3.nc
```

This command uses the `cdsapi` to download the CAMS ADS data.

**Note:**
From the logs that this command has spawned, you can see that the data has been downloaded and unpacked in a specific location in your machine. For example, I'm using a Linux based system so the data has been saved inside a hidden folder in my `$HOME` path. If you're using Windows, it will be downloaded inside a folder in your `%LOCALAPPDATA%` path.

Once you've downloaded the data, you can read it as an `xarray.Dataset` using the `read_dataset` command

```python
eac4.read_dataset()

xarray.Dataset
...
```

You can list all data files downloaded for each dataset using `.list_data_files()`

```python
eac4.list_data_files()
```

When you're done using the application, you can clear all your data using `.clear_data_files()`

```python
eac4.clear_data_files()
```

### Selection

The next concept is the `Selection`, which can be accessed in submodule `atmospheric_explorer.api.shape_selection`. The `Selection` class and its subclasses manage selections of countries, continents etc. but also generic shapes on a map. When you select a country or draw a generic shape on the UI, a `Selection` object is created, but you can also manually create them using the APIs.

There are two classes provided:
- `GenericShapeSelection`: represent a generic shape on the map, not directly corresponding to any entity
- `EntitySelection`: a specific entity or entities, namely countries, continents or sub-national divisions

Each of this classes offer multiple functionalities to easily generate them:

```python
# Generate a GenericShapeSelection from a shapely polygon
from atmospheric_explorer.api.shape_selection.shape_selection import GenericShapeSelection
import shapely.geometry
import shapely

poly = GenericShapeSelection.from_shape(shapely.box(0, 0, 10, 10))
```

For the `EntitySelection` we also have to specify a `SelectionLevel`, which is just an `Enum` defining whether the selection is on continents, countries etc.

```python
from atmospheric_explorer.api.shape_selection.config import SelectionLevel

print(list(SelectionLevel))

[
    <SelectionLevel.GENERIC: 'Generic'>,
    <SelectionLevel.CONTINENTS: 'Continents'>,
    <SelectionLevel.ORGANIZATIONS: 'Organizations'>,
    <SelectionLevel.COUNTRIES: 'Countries'>,
    <SelectionLevel.COUNTRIES_SUB: 'Sub-national divisions'>
]
```

The `Generic` level is only there for compatibility between `EntitySelection` and `GenericShapeSelection` and it shouldn't be used.

```python
from atmospheric_explorer.api.shape_selection.shape_selection import EntitySelection
from atmospheric_explorer.api.shape_selection.config import SelectionLevel

# Generate EntitySelection from a list of countries
sel1 = EntitySelection.from_entities_list(
    ['Italy', 'Germany'],
    SelectionLevel.COUNTRIES
)

# Generate a new EntitySelection with all continents included in the previous selection
## Convert sel1 to the CONTINENTS level
## This will select all continents which intersects sel1
sel2 = EntitySelection.from_entity_selection(
    sel1,
    SelectionLevel.CONTINENTS
)
sel2.labels

['Europe']
```

Use `selection.labels` to see all names of the entities included in the `EntitySelection`.

You can also convert a `GenericShapeSelection` to an `EntitySelection` and viceversa

```python
# Generate a generic shape using shapely polygons
gen_sel = GenericShapeSelection.from_shape(shapely.box(0, 0, 10, 10))
# Convert it to an EntitySelection
## All entities intersected by the shape will be selected
sel = EntitySelection.convert_selection(
    gen_sel,
    SelectionLevel.COUNTRIES
)
sel.labels

['Benin', 'Cameroon', 'Equatorial Guinea', 'Gabon', 'Ghana', 'Nigeria', 'São Tomé and Principe', 'Togo']
```

### Plots

Plotting functionality is provided in the submodule `atmospheric_explorer.api.plotting`. Here you can find a module dedicate to each plot: all plots are built using [Plotly](https://plotly.com/) and each function returns a Plotly `Figure` object, which can then be manipulated as described in the [Plotly documentation](https://plotly.com/python/).

Let's try to generate a yearly flux plot

```python
from atmospheric_explorer.api.plotting.yearly_flux import ghg_surface_satellite_yearly_plot


fig = ghg_surface_satellite_yearly_plot(
    data_variable="carbon_dioxide",
    var_name="flux_foss",
    years=[2018, 2019, 2020, 2021],
    months=["01", "02", "03", "04"],
    title="Carbon dioxide"
)
# fig is a plotly Figure
print(type(fig))

<class 'plotly.graph_objs._figure.Figure'>

# Show the figure on a notebook
fig.show()

# Save the figure to a PNG
fig.write_image("plot.png")
```

Plotly images are interactive and can also be saved to HTML in order to keep all metadata and functionalities

```python
# Save Plotly figure to HTML
fig.write_html("plot.html")
# Now you can open plot.html using a browser
```

Let's add a selection

```python
from atmospheric_explorer.api.shape_selection.shape_selection import EntitySelection
from atmospheric_explorer.api.shape_selection.config import SelectionLevel
from atmospheric_explorer.api.plotting.yearly_flux import ghg_surface_satellite_yearly_plot

sel = EntitySelection.from_entities_list(
    ['Italy', 'Germany'],
    SelectionLevel.COUNTRIES
)

fig = ghg_surface_satellite_yearly_plot(
    data_variable="carbon_dioxide",
    var_name="flux_foss",
    years=[2018, 2019, 2020, 2021],
    months=["01", "02", "03", "04"],
    title="Carbon dioxide",
    shapes=sel
)
fig.show()
```

# How to contribute
See the **APIs** section above for a quick summary about the API functions that you might want to edit and expand.

If you also want to contribute to the project besides using it as a user, you must also install `dev-requirements` running this command (after having activated the `atmospheric-explorer` virtual environment):

```bash
$ pip install -r dev-requirements.txt
```

When you add any new code to the APIs, you will probably also want to include it in the **CLI** and **UI** in their respective folders. The CLI is built using [Click](https://click.palletsprojects.com/en/8.1.x/) and the UI is built using [Streamlit](https://streamlit.io/), so a basic knowledge of these packages is required.

One important point to raise is that both the CLI and the UI only use functions from the APIs and generate barely any logic by themselves. This is a principle to be followed in order to ensure compatibility between the CLI and UI functionalities.

To contribute best, you should also follow the practices described below.

## Pre-commit
This repo uses `pre-commit` to run a number of checks before committing (formatting, linting, tests etc).

In order to enable `pre-commit`, after activating the `atmospheric-explorer` virtual environment, run this command:

```bash
$ pre-commit install
```

Now the checks will run when trying to commit: if any check fails, the changes won't be committed. To see the output of all checks before committing, you can run `pre-commit` in the terminal.

Once pre-commit is enabled, it will run a number of check on **staged files**. All checks should pass before the changes can be commited.

## Logger
The logger configuration is defined in `logger.py` inside a dictionary.

This application uses a logger called `atmexp`, if you want to use it just import it as show below

```python
from atmospheric_explorer.api.loggers import get_logger

logger = get_logger("atmexp")
```

## Sphinx documentation
To update the documentation, you must run the following commands.

1. To re-generate the APIs documentation source `rst` files based on docstrings

    ```bash
    $ sphinx-apidoc -f -o documentation\source\ atmospheric_explorer\api\
    ```

    The first path is where the documentation will be created.

2. To generate the `html` files that make up the documentation, from inside the `documentation` folder run

    ```bash
    make html
    ```

## Unit tests

Most API functionalities are tested using `pytest` inside the `tests` folder. To run the tests and check the code coverage, install the `dev-requirements.txt` as described

```bash
$ pip install -r dev-requirements.txt
$ pytest --cov=atmospheric_explorer --log-disable=true tests/
```
