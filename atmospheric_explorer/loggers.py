"""\
Module to manage logging.
"""
import logging
import logging.config
import os

from .utils import get_local_folder

_LOGGING_CONFIG = {
    "version": 1,
    "loggers": {
        "root": {"handlers": ["console"], "level": "ERROR"},
        "main": {
            "handlers": ["console", "rotatingfile"],
            "level": "DEBUG",
            "propagate": 0,
            "qualname": "main",
        },
    },
    "handlers": {
        "console": {"class": "logging.StreamHandler", "formatter": "simple"},
        "rotatingfile": {
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "verbose",
            "maxBytes": 1024,
            "backupCount": 3,
            "filename": os.path.join(get_local_folder(), "logconfig.log"),
        },
    },
    "formatters": {
        "simple": {"format": "%(levelname)s %(message)s"},
        "verbose": {
            "format": "%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s"  # noqa: E501
        },
    },
}

logging.config.dictConfig(_LOGGING_CONFIG)
# pylint: disable=unused-argument
# ruff: noqa: F401
_main_logger = logging.getLogger("main")
