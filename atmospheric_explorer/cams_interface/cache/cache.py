"""\
This module collects classes to easily interact with data downloaded from CAMS ADS.
"""
# pylint: disable=too-few-public-methods
# pylint: disable=too-many-arguments
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase
from atmospheric_explorer.utils import get_local_folder
import os


DATABASE_FILE = "calls_cache.db"
DATABASE_PATH = os.path.join(get_local_folder(), 'cache', DATABASE_FILE)


class Base(DeclarativeBase):
    pass


url = f"sqlite:///{DATABASE_PATH}"
print(url)
cache_engine = create_engine(url, echo=True)
