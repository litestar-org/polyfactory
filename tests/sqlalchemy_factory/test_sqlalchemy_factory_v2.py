from enum import Enum
from ipaddress import ip_network
from typing import Any, Dict, List
from uuid import UUID

import pytest
from sqlalchemy import ForeignKey, Text, __version__, orm, types
from sqlalchemy.dialects.mssql import JSON as MSSQL_JSON
from sqlalchemy.dialects.mysql import JSON as MYSQL_JSON
from sqlalchemy.dialects.postgresql import ARRAY, CIDR, HSTORE, INET, JSON, JSONB
from sqlalchemy.dialects.sqlite import JSON as SQLITE_JSON
from sqlalchemy.ext.mutable import MutableDict, MutableList

from polyfactory.factories.sqlalchemy_factory import SQLAlchemyFactory

if __version__.startswith("1"):
    pytest.importorskip("SQLAlchemy", "2")


class Base(orm.DeclarativeBase): ...


class Author(Base):
    __tablename__ = "authors"

    id: orm.Mapped[int] = orm.mapped_column(primary_key=True)
    books: orm.Mapped[List["Book"]] = orm.relationship(
        "Book",
        uselist=True,
        back_populates="author",
    )


class Book(Base):
    __tablename__ = "books"

    id: orm.Mapped[int] = orm.mapped_column(primary_key=True)
    author_id: orm.Mapped[int] = orm.mapped_column(ForeignKey(Author.id))
    author: orm.Mapped[Author] = orm.relationship(
        Author,
        uselist=False,
        back_populates="books",
    )


def test_python_type_handling_v2() -> None:
    class Base(orm.DeclarativeBase): ...

    class Animal(str, Enum):
        DOG = "Dog"
        CAT = "Cat"

    class Model(Base):
        __tablename__ = "model"

        id: orm.Mapped[int] = orm.mapped_column(primary_key=True)
        str_type: orm.Mapped[str]
        enum_type: orm.Mapped[Animal]
        str_array_type: orm.Mapped[List[str]] = orm.mapped_column(
            type_=types.ARRAY(types.String),
        )

    class ModelFactory(SQLAlchemyFactory[Model]):
        __model__ = Model

    instance = ModelFactory.build()
    assert isinstance(instance.id, int)
    assert isinstance(instance.str_type, str)
    assert isinstance(instance.enum_type, Animal)
    assert isinstance(instance.str_array_type, list)
    assert isinstance(instance.str_array_type[0], str)


def test_sqla_dialect_types() -> None:
    class Base(orm.DeclarativeBase): ...

    class SqlaModel(Base):
        __tablename__ = "sql_models"
        id: orm.Mapped[int] = orm.mapped_column(primary_key=True)
        uuid_type: orm.Mapped[UUID] = orm.mapped_column(type_=types.UUID)
        nested_array_inet: orm.Mapped[List[str]] = orm.mapped_column(type_=ARRAY(INET, dimensions=1))
        nested_array_cidr: orm.Mapped[List[str]] = orm.mapped_column(type_=ARRAY(CIDR, dimensions=1))
        hstore_type: orm.Mapped[Dict] = orm.mapped_column(type_=HSTORE)
        mut_nested_arry_inet: orm.Mapped[List[str]] = orm.mapped_column(
            type_=MutableList.as_mutable(ARRAY(INET, dimensions=1))
        )
        pg_json_type: orm.Mapped[Dict] = orm.mapped_column(type_=JSON)
        pg_jsonb_type: orm.Mapped[Dict] = orm.mapped_column(type_=JSONB)
        common_json_type: orm.Mapped[Dict] = orm.mapped_column(type_=types.JSON)
        mysql_json: orm.Mapped[Dict] = orm.mapped_column(type_=MYSQL_JSON)
        sqlite_json: orm.Mapped[Dict] = orm.mapped_column(type_=SQLITE_JSON)
        mssql_json: orm.Mapped[Dict] = orm.mapped_column(type_=MSSQL_JSON)

        multible_pg_json_type: orm.Mapped[Dict] = orm.mapped_column(
            type_=MutableDict.as_mutable(JSON(astext_type=Text()))  # type: ignore[no-untyped-call]
        )
        multible_pg_jsonb_type: orm.Mapped[Dict] = orm.mapped_column(
            type_=MutableDict.as_mutable(JSONB(astext_type=Text()))  # type: ignore[no-untyped-call]
        )
        multible_common_json_type: orm.Mapped[Dict] = orm.mapped_column(type_=MutableDict.as_mutable(types.JSON()))
        multible_mysql_json: orm.Mapped[Dict] = orm.mapped_column(type_=MutableDict.as_mutable(MYSQL_JSON()))
        multible_sqlite_json: orm.Mapped[Dict] = orm.mapped_column(type_=MutableDict.as_mutable(SQLITE_JSON()))
        multible_mssql_json: orm.Mapped[Dict] = orm.mapped_column(type_=MutableDict.as_mutable(MSSQL_JSON()))

    class ModelFactory(SQLAlchemyFactory[SqlaModel]):
        __model__ = SqlaModel

    instance = ModelFactory.build()
    assert isinstance(instance.nested_array_inet[0], str)
    assert ip_network(instance.nested_array_inet[0])
    assert isinstance(instance.nested_array_cidr[0], str)
    assert ip_network(instance.nested_array_cidr[0])
    assert isinstance(instance.hstore_type, dict)
    assert isinstance(instance.uuid_type, UUID)
    assert isinstance(instance.mut_nested_arry_inet[0], str)
    assert ip_network(instance.mut_nested_arry_inet[0])
    assert isinstance(instance.pg_json_type, dict)
    for value in instance.pg_json_type.values():
        assert isinstance(value, (str, int, bool, float))
    assert isinstance(instance.pg_jsonb_type, dict)
    for value in instance.pg_jsonb_type.values():
        assert isinstance(value, (str, int, bool, float))
    assert isinstance(instance.common_json_type, dict)
    for value in instance.common_json_type.values():
        assert isinstance(value, (str, int, bool, float))
    assert isinstance(instance.mysql_json, dict)
    for value in instance.mysql_json.values():
        assert isinstance(value, (str, int, bool, float))
    assert isinstance(instance.sqlite_json, dict)
    for value in instance.sqlite_json.values():
        assert isinstance(value, (str, int, bool, float))
    assert isinstance(instance.mssql_json, dict)
    for value in instance.mssql_json.values():
        assert isinstance(value, (str, int, bool, float))
    assert isinstance(instance.multible_pg_json_type, dict)
    assert isinstance(instance.multible_pg_jsonb_type, dict)
    assert isinstance(instance.multible_common_json_type, dict)
    assert isinstance(instance.multible_mysql_json, dict)
    assert isinstance(instance.multible_sqlite_json, dict)
    assert isinstance(instance.multible_mssql_json, dict)


@pytest.mark.parametrize(
    "type_",
    tuple(SQLAlchemyFactory.get_sqlalchemy_types().keys()),
)
def test_sqlalchemy_type_handlers_v2(type_: types.TypeEngine) -> None:
    class Base(orm.DeclarativeBase): ...

    class Model(Base):
        __tablename__ = "model_with_overriden_type"

        id: orm.Mapped[int] = orm.mapped_column(primary_key=True)
        overridden: orm.Mapped[Any] = orm.mapped_column(type_=type_)

    class ModelFactory(SQLAlchemyFactory[Model]):
        __model__ = Model

    instance = ModelFactory.build()
    assert instance.overridden is not None
