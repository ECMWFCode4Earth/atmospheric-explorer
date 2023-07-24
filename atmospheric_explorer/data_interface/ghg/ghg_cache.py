"""\
This module collects classes to easily interact with data downloaded from CAMS ADS.
"""
# pylint: disable=too-few-public-methods
# pylint: disable=too-many-arguments
from __future__ import annotations

from textwrap import dedent

from sqlalchemy import Integer, String, delete, select
from sqlalchemy.dialects.sqlite import insert as sqlite_upsert
from sqlalchemy.orm import Session, mapped_column

from atmospheric_explorer.data_interface.cache import Base, cache_engine
from atmospheric_explorer.data_interface.ghg.ghg_parameters import GHGParameters
from atmospheric_explorer.loggers import get_logger

logger = get_logger("atmexp")


class GHGCacheTable(Base):
    """Table used to cache GHG calls and retrieve file paths related to each data point."""
    __tablename__ = "ghg_cache_table"
    data_variables = mapped_column(String(30), primary_key=True)
    file_format = mapped_column(String(10), primary_key=True)
    quantity = mapped_column(String(30), primary_key=True)
    input_observations = mapped_column(String(30), primary_key=True)
    time_aggregation = mapped_column(String(30), primary_key=True)
    year = mapped_column(Integer, primary_key=True)
    month = mapped_column(Integer, primary_key=True)
    version = mapped_column(String(10), primary_key=True)
    files_path = mapped_column(String, nullable=False, unique=False)

    def __repr__(self) -> str:
        return dedent(
            f"""
            'data_variables': {self.data_variables},
            'file_format': {self.file_format},
            'quantity': {self.quantity},
            'input_observations': {self.input_observations},
            'time_aggregation': {self.time_aggregation},
            'year': {self.year},
            'month': {self.month},
            'version': {self.version},
            'files_path': {self.files_path},
        """
        )

    @classmethod
    def get_rows(cls, parameters: GHGParameters | None = None) -> list[dict]:
        """Get rows from the table. If a parameter instance is passed, all rows with the same variables are returned."""
        with Session(cache_engine) as session:
            if parameters is not None:
                return [
                    row._mapping[cls]
                    for row in session.execute(
                        select(cls).where(
                            cls.data_variables == parameters.data_variables,
                            cls.file_format == parameters.file_format,
                            cls.quantity == parameters.quantity,
                            cls.input_observations == parameters.input_observations,
                            cls.time_aggregation == parameters.time_aggregation,
                            cls.version == parameters.version,
                            cls.year.in_(parameters._years),
                            cls.month.in_(parameters._months),
                        )
                    ).all()
                ]
            else:
                return [row._mapping[cls] for row in session.execute(select(cls)).all()]

    @classmethod
    def cache(cls, parameters: GHGParameters, files_path: str | None = None) -> None:
        """Caches a parameters object using an upsert on key variables."""
        upsert_stmt = sqlite_upsert(cls).values(
            [
                {
                    "data_variables": parameters.data_variables,
                    "file_format": parameters.file_format,
                    "quantity": parameters.quantity,
                    "input_observations": parameters.input_observations,
                    "time_aggregation": parameters.time_aggregation,
                    "year": y,
                    "month": m,
                    "version": parameters.version,
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
    def get_files(cls, parameters: list[GHGParameters]) -> list:
        """Given a list of parameters, return all files associated."""
        years = set()
        months = set()
        for p in parameters:
            years.update(p._years)
            months.update(p._months)
        with Session(cache_engine) as session:
            return session.scalars(
                select(cls.files_path)
                .distinct()
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
            ).all()

    @classmethod
    def delete_rows(cls, parameters: list[GHGParameters]):
        years = set()
        months = set()
        for p in parameters:
            years.update(p._years)
            months.update(p._months)
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
    p1 = GHGParameters(
        data_variables="a",
        file_format="b",
        quantity="c",
        input_observations="d",
        time_aggregation="e",
        years=[2020, 2021],
        months=[1, 2],
    )
    p2 = GHGParameters(
        data_variables="a",
        file_format="b",
        quantity="c",
        input_observations="d",
        time_aggregation="e",
        years=[2020, 2021, 2022],
        months=[3],
    )
    p3 = GHGParameters(
        data_variables="a",
        file_format="b",
        quantity="c",
        input_observations="d",
        time_aggregation="e",
        years=[2020, 2021, 2022],
        months=[1, 2, 3],
    )
    GHGCacheTable.cache(p1, "file")
    GHGCacheTable.cache(p2, "file2")
    print(GHGCacheTable.get_rows())
    print(GHGCacheTable.get_files([p1, p2]))
