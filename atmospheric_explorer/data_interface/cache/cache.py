"""\
This module collects classes to easily interact with data downloaded from CAMS ADS.
"""
from __future__ import annotations
import os

# pylint: disable=too-few-public-methods
# pylint: disable=too-many-arguments
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase
from enum import Enum
from atmospheric_explorer.utils import get_local_folder

from sqlalchemy import Integer, String, delete, select
from sqlalchemy.dialects.sqlite import insert as sqlite_upsert
from sqlalchemy.orm import Session, mapped_column
from textwrap import dedent

from atmospheric_explorer.data_interface.cams_interface.cams_parameters import CAMSParameters

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


class CacheTable(Base):
    """Table used to cache GHG calls and retrieve file paths related to each data point."""
    __tablename__ = ""
    file_format = mapped_column(String(10), primary_key=True)

    @classmethod
    def get_rows(cls, parameters: CAMSParameters | None = None) -> list[dict]:
        """Get rows from the table. If a parameter instance is passed, all rows with the same variables are returned."""
        with Session(cache_engine) as session:
            if parameters is not None:
                sel = select(cls)
                for field_name in parameters:
                    sel = sel.where(getattr(cls, field_name) == getattr(parameters, field_name).value)
                return [
                    row._mapping[cls]
                    for row in session.execute(sel).all()
                ]
            else:
                return [row._mapping[cls] for row in session.execute(select(cls)).all()]

    @classmethod
    def cache(cls, parameters: CAMSParameters, files_path: str | None = None) -> None:
        """Caches a parameters object using an upsert on key variables."""
        upsert_stmt = sqlite_upsert(cls).values(
            [
                {
                    "data_variables": parameters.data_variables.value,
                    "file_format": parameters.file_format.value,
                    "quantity": parameters.quantity.value,
                    "input_observations": parameters.input_observations.value,
                    "time_aggregation": parameters.time_aggregation.value,
                    "year": y,
                    "month": m,
                    "version": parameters.version.value,
                    "files_path": files_path,
                }
                for y, m in parameters.years_months()
            ]
        )
        upsert_stmt = upsert_stmt.on_conflict_do_update(
            index_elements=[
                cls.data_variables,
                cls.file_format,
                cls.quantity,
                cls.input_observations,
                cls.time_aggregation,
                cls.year,
                cls.month,
                cls.version,
            ],
            set_={"files_path": upsert_stmt.excluded.files_path},
        )
        with Session(cache_engine) as session:
            session.execute(upsert_stmt)
            session.commit()

    @classmethod
    def get_files(cls, parameters: list[CAMSParameters]) -> list:
        """Given a list of parameters, return all files associated."""
        years = set()
        months = set()
        for p in parameters:
            years.update(p.years.value)
            months.update(p.months.value)
        with Session(cache_engine) as session:
            return session.scalars(
                select(cls.files_path)
                .distinct()
                .where(
                    cls.data_variables.in_({p.data_variables.value for p in parameters}),
                    cls.file_format.in_({p.file_format.value for p in parameters}),
                    cls.quantity.in_({p.quantity.value for p in parameters}),
                    cls.input_observations.in_(
                        {p.input_observations.value for p in parameters}
                    ),
                    cls.time_aggregation.in_({p.time_aggregation.value for p in parameters}),
                    cls.version.in_({p.version.value for p in parameters}),
                    cls.year.in_(years),
                    cls.month.in_(months),
                )
            ).all()

    @classmethod
    def delete_rows(cls, parameters: list[CAMSParameters]):
        years = set()
        months = set()
        for p in parameters:
            years.update(p.years.value)
            months.update(p.months.value)
        with Session(cache_engine) as session:
            session.execute(
                delete(cls)
                .where(
                    cls.data_variables.in_({p.data_variables for p in parameters}),
                    cls.file_format.in_({p.file_format for p in parameters}),
                    cls.quantity.in_({p.quantity for p in parameters}),
                    cls.input_observations.in_(
                        {p.input_observations for p in parameters}
                    ),
                    cls.time_aggregation.in_({p.time_aggregation for p in parameters}),
                    cls.version.in_({p.version for p in parameters}),
                    cls.year.in_(years),
                    cls.month.in_(months),
                )
            )
            session.commit()

    @classmethod
    def drop(cls):
        """Drop table"""
        with Session(cache_engine) as session:
            session.execute(delete(cls))
            session.commit()


if __name__ == "__main__":
    Base.metadata.drop_all(cache_engine)
    Base.metadata.create_all(cache_engine)
    p1 = CAMSParameters(
        file_format="b"
    )
    p2 = CAMSParameters(
        file_format="b"
    )
    p3 = CAMSParameters(
        file_format="b"
    )
    CacheTable.cache(p1, "file")
    CacheTable.cache(p2, "file2")
    print(CacheTable.get_rows())
    print(CacheTable.get_files([p1, p2]))
