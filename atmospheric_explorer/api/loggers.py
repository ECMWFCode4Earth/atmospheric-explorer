"""\
Module to manage logging.
"""
import logging
import logging.config
import os

from atmospheric_explorer.api.os_manager import create_folder, get_local_folder


class LoggersMeta(type):
    # pylint: disable=too-few-public-methods
    """\
    This meta class is needed to implement a singleton pattern so that
    the logger config is loaded only once.
    """
    _instances = {}
    logs_root_dir = os.path.join(get_local_folder(), "logs")
    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "loggers": {
            "root": {"handlers": logging.root.handlers, "level": "WARNING"},
            "atmexp": {
                "handlers": ["console", "rotatingfile"],
                "level": "INFO",
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
                "backupCount": 20,
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
        create_folder(cls.logs_root_dir)
        logging.config.dictConfig(cls.logging_config)
        super().__init__(*args, **kwargs)

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class Loggers(metaclass=LoggersMeta):
    # pylint: disable=too-few-public-methods
    """\
    This class is needed to implement a singleton pattern so that
    the logger config is loaded only once.
    """

    @classmethod
    def get_logger(cls, logger: str):
        """Function to get a logger"""
        return logging.getLogger(logger)


# pylint: disable=unused-argument
# ruff: noqa: F401
def get_logger(logger: str):
    """Function to get a logger"""
    return Loggers.get_logger(logger)
