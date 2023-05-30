"""Module to manage constants"""

import configparser


class ConstantsMeta(type):
    # pylint: disable=too-few-public-methods
    """\
    This meta class is needed to implement a singleton pattern so that
    constants are loaded only once.
    """
    _instances = {}

    def __init__(cls, *args, **kwargs):
        cls.constants = configparser.ConfigParser()
        cls.constants.read("./constants.cfg")
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
    """Function to get the actual constants object."""
    return Constants.get_constants()
