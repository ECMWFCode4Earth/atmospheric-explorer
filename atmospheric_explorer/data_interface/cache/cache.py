"""\
This module collects classes to easily interact with data downloaded from CAMS ADS.
"""
import os

# pylint: disable=too-few-public-methods
# pylint: disable=too-many-arguments
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase
from enum import Enum
from atmospheric_explorer.utils import get_local_folder

DATABASE_FILE = "calls_cache.db"
DATABASE_PATH = os.path.join(get_local_folder(), "cache", DATABASE_FILE)
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"
cache_engine = create_engine(DATABASE_URL, echo=True)


class Base(DeclarativeBase):
    pass


class CachingStatus(Enum):
    UNCACHED = 1
    PARTIALLY_CACHED = 2
    FULLY_CACHED = 3
