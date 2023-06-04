"""\
Module to manage constants.
This module defines a Singleton, in this way the file constants.cfg is loaded only once.
"""

import configparser
import logging
import logging.config
import os

from ..config import LOGGING

logging.config.dictConfig(LOGGING)
logger = logging.getLogger("mainlogger")


class ConstantsMeta(type):
    # pylint: disable=too-few-public-methods
    """\
    This meta class is needed to implement a singleton pattern so that
    constants are loaded only once.
    """
    _instances = {}

    def __init__(cls, *args, **kwargs):
        filepath = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "constants.cfg"
        )
        cls.constants = configparser.ConfigParser()
        cls.constants.read(filepath)
        logger.info("Loaded constants from file constants.cfg")
        super().__init__(*args, **kwargs)

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class Constants(metaclass=ConstantsMeta):
    # pylint: disable=too-few-public-methods
    """\
    This class is needed to implement a singleton pattern so that
    constants are loaded only once.
    """

    @classmethod
    def get_constants(cls):
        """Function to get the actual constants object."""
        return cls().constants


def get_constants():
    """Function to get the actual constants object from the singleton class."""
    return Constants.get_constants()
