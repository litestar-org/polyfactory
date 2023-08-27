from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional

import pytest
from sqlalchemy import ForeignKey, orm, types
from sqlalchemy.orm import mapped_column

from polyfactory.exceptions import ConfigurationException
from polyfactory.factories.sqlalchemy_factory import SQLAlchemyFactory


def test_invalid_model() -> None:
    class Base(orm.DeclarativeBase):
        ...

    @dataclass
    class NonSQLAchemyClass:
        id_: int

    for invalid in (
        Base,
        NonSQLAchemyClass,
    ):
        with pytest.raises(ConfigurationException):
            SQLAlchemyFactory.create_factory(invalid)


def test_python_type_handling() -> None:
    class Base(orm.DeclarativeBase):
        ...

    class Animal(str, Enum):
        DOG = "Dog"
        CAT = "Cat"

    class Model(Base):
        __tablename__ = "model"

        id: orm.Mapped[int] = mapped_column(primary_key=True)
        str_type: orm.Mapped[str] = mapped_column(nullable=False)
        enum_type: orm.Mapped[Animal]
        str_array_type: orm.Mapped[list[str]] = mapped_column(type_=types.ARRAY(types.String))

    class ModelFactory(SQLAlchemyFactory[Model]):
        __model__ = Model

    instance = ModelFactory.build()
    assert isinstance(instance.id, int)
    assert isinstance(instance.str_type, str)
    assert isinstance(instance.enum_type, Animal)
    assert isinstance(instance.str_array_type, list)
    assert isinstance(instance.str_array_type[0], str)


@pytest.mark.parametrize(
    "type_",
    tuple(
        SQLAlchemyFactory.get_sqlalchemy_types().keys(),
    ),
)
def test_sqlalchemy_type_handlers(type_: types.TypeEngine) -> None:
    class Base(orm.DeclarativeBase):
        ...

    class Model(Base):
        __tablename__ = "model"

        id: orm.Mapped[int] = mapped_column(primary_key=True)
        overridden: orm.Mapped[Any] = mapped_column(type_=type_)

    class ModelFactory(SQLAlchemyFactory[Model]):
        __model__ = Model

    instance = ModelFactory.build()
    assert instance.overridden is not None


def test_optional_field() -> None:
    class Base(orm.DeclarativeBase):
        ...

    class Model(Base):
        __tablename__ = "model"

        id: orm.Mapped[int] = mapped_column(primary_key=True)
        optional_field: orm.Mapped[Optional[str]]

    class ModelFactory(SQLAlchemyFactory[Model]):
        __model__ = Model

    failed = True
    for _ in range(10):
        try:
            result = ModelFactory.build()
            assert result.optional_field is None
            failed = False
            break
        except AssertionError:
            continue

    assert not failed


def test_ignore_primary_key() -> None:
    class Base(orm.DeclarativeBase):
        ...

    class Model(Base):
        __tablename__ = "model"

        id: orm.Mapped[int] = mapped_column(primary_key=True)
        optional_field: orm.Mapped[Optional[str]]

    class ModelFactory(SQLAlchemyFactory[Model]):
        __model__ = Model
        __resolve_primary_key__ = False

    result = ModelFactory.build()
    assert result.id is None


class Base(orm.DeclarativeBase):
    ...


class Author(Base):
    __tablename__ = "authors"

    id: orm.Mapped[int] = mapped_column(primary_key=True)
    books: orm.Mapped[list["Book"]] = orm.relationship(
        "Book",
        uselist=True,
        back_populates="author",
    )


class Book(Base):
    __tablename__ = "books"

    id: orm.Mapped[int] = mapped_column(primary_key=True)
    author_id: orm.Mapped[Optional[int]] = mapped_column(ForeignKey(Author.id))
    author: orm.Mapped[Author] = orm.relationship(
        Author,
        uselist=False,
        back_populates="books",
    )


def test_relationship_resolution() -> None:
    class BookFactory(SQLAlchemyFactory[Book]):
        __model__ = Book
        __resolve_foreign_keys__ = False
        __resolve_relationships__ = True

    result = BookFactory.build()
    assert result.author_id is None
    assert isinstance(result.author, Author)


def test_relationship_list_resolution() -> None:
    class AuthorFactory(SQLAlchemyFactory[Author]):
        __model__ = Author
        __resolve_foreign_keys__ = False
        __resolve_relationships__ = True

    result = AuthorFactory.build()
    assert isinstance(result.books, list)


def test_alias() -> None:
    class Base(orm.DeclarativeBase):
        ...

    class ModelWithAlias(Base):
        __tablename__ = "table"

        id: orm.Mapped[int] = mapped_column(primary_key=True)
        name: orm.Mapped[str] = mapped_column("alias")

    class ModelFactory(SQLAlchemyFactory[ModelWithAlias]):
        __model__ = ModelWithAlias

    result = ModelFactory.build()
    assert isinstance(result.name, str)
