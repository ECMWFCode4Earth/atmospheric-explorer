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
    """Table used to cache EAC4 calls and retrieve file paths related to each data point."""
    __tablename__ = "eac4_cache_table"
    param_id = mapped_column(Integer, nullable=False, unique=False)
    data_variables = mapped_column(String(30), primary_key=True)
    day = mapped_column(Date, primary_key=True)
    time = mapped_column(String(5), primary_key=True)
    pressure_level = mapped_column(Integer, primary_key=True, default=-1)
    model_level = mapped_column(Integer, primary_key=True, default=-1)
    files_path = mapped_column(String, nullable=False, unique=False)

    def __repr__(self) -> str:
        return dedent(
            f"""
            'param_id': {self.param_id},
            'data_variables': {self.data_variables},
            'day': {self.day},
            'time': {self.time},
            'pressure_level': {self.pressure_level},
            'model_level': {self.model_level},
            'files_path': {self.files_path},
        """
        )

    @classmethod
    def _filter_parameters(cls, stmt, parameters: list[EAC4Parameters]):
        p = EAC4Parameters.merge(parameters)
        return stmt.where(
            cls.data_variables.in_(p.data_variables.value),
            cls.pressure_level.in_(p.pressure_level.value),
            cls.model_level.in_(p.model_level.value),
            cls.time.in_(p.time_values),
            cls.day.between(p.dates_range.start, p.dates_range.end)
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
                    "param_id": id(parameters),
                    "data_variables": dv,
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
                cls.day,
                cls.time,
                cls.pressure_level,
                cls.model_level
            ],
            set_={
                "param_id": upsert_stmt.excluded.param_id,
                "files_path": upsert_stmt.excluded.files_path
            },
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
        dates_range="2021-01-01/2021-01-05",
        time_values="00:00"
    )
    p2 = EAC4Parameters.from_base_types(
        data_variables="a",
        dates_range="2021-01-04/2021-02-05",
        time_values="00:00"
    )
    EAC4CacheTable.cache(p1, "file")
    EAC4CacheTable.cache(p2, "file2")
    print(EAC4CacheTable.get_rows())
    print(EAC4CacheTable.get_files([p1, p2]))
