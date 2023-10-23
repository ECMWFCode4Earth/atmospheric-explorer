# pylint: disable=missing-module-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=unused-import
# ruff: noqa: F401
import logging

import pytest

# this import is needed because otherwise the atmexp logger won't be instantiated when disabling the logs
from atmospheric_explorer.api.loggers.loggers import atm_exp_logger


@pytest.fixture(autouse=True, scope="session")
def disable_logging():
    logging.disable(logging.CRITICAL)
    yield
    logging.disable(logging.NOTSET)
