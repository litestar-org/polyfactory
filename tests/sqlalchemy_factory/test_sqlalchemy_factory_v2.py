from enum import Enum
from ipaddress import ip_network
from typing import Any, List

import pytest
from sqlalchemy import ForeignKey, __version__, orm, types
from sqlalchemy.dialects.postgresql import ARRAY, CIDR, HSTORE, INET, JSON, JSONB

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


def test_pg_dialect_types() -> None:
    class Base(orm.DeclarativeBase): ...

    class PgModel(Base):
        __tablename__ = "pgmodel"
        id: orm.Mapped[int] = orm.mapped_column(primary_key=True)
        nested_array_inet: orm.Mapped[List[str]] = orm.mapped_column(type_=ARRAY(INET, dimensions=1))
        nested_array_cidr: orm.Mapped[list[str]] = orm.mapped_column(type_=ARRAY(CIDR, dimensions=1))
        hstore_type: orm.Mapped[dict] = orm.mapped_column(type_=HSTORE)
        pg_json_type: orm.Mapped[dict] = orm.mapped_column(type_=JSON)
        pg_jsonb_type: orm.Mapped[dict] = orm.mapped_column(type_=JSONB)

    class ModelFactory(SQLAlchemyFactory[PgModel]):
        __model__ = PgModel

    instance = ModelFactory.build()

    assert isinstance(instance.nested_array_inet[0], str)
    assert ip_network(instance.nested_array_inet[0])
    assert isinstance(instance.nested_array_cidr[0], str)
    assert ip_network(instance.nested_array_cidr[0])
    assert isinstance(instance.hstore_type, dict)
    assert isinstance(instance.pg_json_type, dict)
    assert isinstance(instance.pg_json_type, dict)


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
