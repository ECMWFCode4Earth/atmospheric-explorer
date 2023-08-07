"""\
This module collects classes to easily interact with data downloaded from CAMS ADS.
"""
# pylint: disable=too-few-public-methods
# pylint: disable=too-many-arguments
from __future__ import annotations

from textwrap import dedent

from sqlalchemy import Integer, String, delete, select, Date
from sqlalchemy.dialects.sqlite import insert as sqlite_upsert
from sqlalchemy.orm import Session, mapped_column

from atmospheric_explorer.data_interface.cache import Base, cache_engine
from atmospheric_explorer.data_interface.eac4.eac4_parameters import EAC4Parameters
from atmospheric_explorer.loggers import get_logger
from itertools import product

logger = get_logger("atmexp")


class EAC4CacheTable(Base):
    """Table used to cache GHG calls and retrieve file paths related to each data point."""
    __tablename__ = "eac4_cache_table"
    data_variables = mapped_column(String(30), primary_key=True)
    file_format = mapped_column(String(10), primary_key=True)
    day = mapped_column(Date, primary_key=True)
    time = mapped_column(String(5), primary_key=True)
    pressure_level = mapped_column(Integer, primary_key=True, default=-1)
    model_level = mapped_column(Integer, primary_key=True, default=-1)
    files_path = mapped_column(String, nullable=False, unique=False)

    def __repr__(self) -> str:
        return dedent(
            f"""
            'data_variables': {self.data_variables},
            'file_format': {self.file_format},
            'day': {self.day},
            'time': {self.time},
            'pressure_level': {self.pressure_level},
            'model_level': {self.model_level},
            'files_path': {self.files_path},
        """
        )

    @classmethod
    def _filter_parameters(cls, stmt, parameters: list[EAC4Parameters]):
        dv = set()
        pl = set()
        ml = set()
        times = set()
        dates = parameters[0].dates_range
        for p in parameters:
            dv.update(p.data_variables.value)
            pl.update(p.pressure_level.value if p.pressure_level is not None else [-1])
            ml.update(p.model_level.value if p.model_level is not None else [-1])
            times.update(p.time_values.value)
            dates = dates.merge(p.dates_range)
        return stmt.where(
            cls.file_format.in_({p.file_format.value for p in parameters}),
            cls.data_variables.in_(dv),
            cls.pressure_level.in_(pl),
            cls.model_level.in_(ml),
            cls.time.in_(times),
            cls.day.between(dates.start, dates.end)
        )

    @classmethod
    def get_rows(cls, parameters: list[EAC4Parameters] | None = None) -> list[dict]:
        """Get rows from the table. If a parameter instance is passed, all rows with the same variables are returned."""
        with Session(cache_engine) as session:
            if parameters is not None:
                stmt = cls._filter_parameters(select(cls), parameters)
                return [
                    row._mapping[cls]
                    for row in session.execute(stmt).all()
                ]
            else:
                return [row._mapping[cls] for row in session.execute(select(cls)).all()]

    @classmethod
    def cache(cls, parameters: EAC4Parameters, files_path: str | None = None) -> None:
        """Caches a parameters object using an upsert on key variables."""
        upsert_stmt = sqlite_upsert(cls).values(
            [
                {
                    "data_variables": dv,
                    "file_format": parameters.file_format.value,
                    "day": day,
                    "time": time,
                    "pressure_level": pl,
                    "model_level": ml,
                    "files_path": files_path

                }
                for dv, day, time, pl, ml in product(
                    parameters.data_variables.value,
                    parameters.dates_range.all_days,
                    parameters.time_values.value,
                    parameters.pressure_level.value if parameters.pressure_level is not None else [-1],
                    parameters.model_level.value if parameters.model_level is not None else [-1]
                )
            ]
        )
        upsert_stmt = upsert_stmt.on_conflict_do_update(
            index_elements=[
                cls.data_variables,
                cls.file_format,
                cls.day,
                cls.time,
                cls.pressure_level,
                cls.model_level
            ],
            set_={"files_path": upsert_stmt.excluded.files_path},
        )
        with Session(cache_engine) as session:
            session.execute(upsert_stmt)
            session.commit()

    @classmethod
    def get_files(cls, parameters: list[EAC4Parameters]) -> list:
        """Given a list of parameters, return all files associated."""
        stmt = select(cls.files_path).distinct()
        stmt = cls._filter_parameters(stmt, parameters)
        with Session(cache_engine) as session:
            return session.scalars(stmt).all()

    @classmethod
    def delete_rows(cls, parameters: list[EAC4Parameters]):
        with Session(cache_engine) as session:
            session.execute(cls._filter_parameters(delete(cls), parameters))
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
    p1 = EAC4Parameters.from_base_types(
        data_variables="a",
        file_format="b",
        dates_range="2021-01-01/2021-01-05",
        time_values="00:00"
    )
    p2 = EAC4Parameters.from_base_types(
        data_variables="a",
        file_format="b",
        dates_range="2021-01-04/2021-02-05",
        time_values="00:00"
    )
    EAC4CacheTable.cache(p1, "file")
    EAC4CacheTable.cache(p2, "file2")
    print(EAC4CacheTable.get_rows())
    print(EAC4CacheTable.get_files([p1, p2]))
