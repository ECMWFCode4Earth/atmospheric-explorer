# atmospheric-explorer

Repository for 2023 Code for Earth project to develop a tool for exploration of CAMS atmospheric composition datasets.

# How to use pre-commit to contribute

This repo uses `pre-commit` to run a number of checks before committing (formatting, linting, tests ecc.). In order to enable `pre-commit`:
- In a terminal, create an python env using the command `conda env create -f env.yml`
- Activate the environment with `conda activate atmospheric-explorer`
- Run `pre-commit install`
- Now the checks will run when trying to commit, if any check fails the changes won't be committed
- To see the output of all checks before committing, you can run `pre-commit` in a terminal

Once pre-commit is enabled, it will run a number of check on **staged files**. All checks should pass before the changes can be commited.

# How to use the logger
The logger configuration is defined in `logger.py` inside a dictionary.

At the moment we only have one logger called `main`, if you want to use it just import it as show below
```
from .loggers import get_logger
logger = get_logger("main")
```

# How to run the Streamlit application

To run the streamlit application, install the package with

```pip install -e .```

and run in the terminal the command

```atmospheric-explorer```
