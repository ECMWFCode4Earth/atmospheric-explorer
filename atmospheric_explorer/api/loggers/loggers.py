"""Module to manage logging."""
import logging
import logging.config
import os

from atmospheric_explorer.api.local_folder import get_local_folder
from atmospheric_explorer.api.singleton import Singleton


class LoggerSingleton(Singleton):
    # pylint: disable=too-few-public-methods
    """This meta class is needed to implement a singleton pattern so that the logger config is loaded only once."""
    logs_root_dir = os.path.join(get_local_folder(), "logs")
    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "loggers": {
            "root": {"handlers": logging.root.handlers, "level": "WARNING"},
            "atmexp": {
                "handlers": ["console", "rotatingfile"],
                "level": "DEBUG",
                "propagate": 0,
                "qualname": "atmexp",
            },
        },
        "handlers": {
            "console": {"class": "logging.StreamHandler", "formatter": "simple"},
            "rotatingfile": {
                "class": "logging.handlers.RotatingFileHandler",
                "formatter": "verbose",
                "maxBytes": 51200,
                "backupCount": 100,
                "filename": os.path.join(logs_root_dir, "logconfig.log"),
            },
        },
        "formatters": {
            "simple": {"format": "%(asctime)s %(levelname)s %(message)s"},
            "verbose": {
                "format": "%(asctime)s|%(levelname)s|%(module)s|%(process)d|%(thread)d: %(message)s"  # noqa: E501
            },
        },
    }

    def __init__(cls, *args, **kwargs):
        # pylint: disable = unused-argument
        if not os.path.exists(cls.logs_root_dir):
            os.makedirs(cls.logs_root_dir)
        logging.config.dictConfig(cls.logging_config)


class Logger(metaclass=LoggerSingleton):
    # pylint: disable=too-few-public-methods
    """Class need to implement the singleton pattern for the logger configuration."""

    @classmethod
    def get_logger(cls):
        """Function to get a logger."""
        return logging.getLogger("atmexp")


# pylint: disable=unused-argument
# ruff: noqa: F401
atm_exp_logger = Logger.get_logger()
