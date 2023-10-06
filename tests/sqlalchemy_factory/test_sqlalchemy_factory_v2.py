import datetime
from collections.abc import Callable
from enum import Enum
from typing import Any, List

import pytest
from sqlalchemy import ForeignKey, __version__, orm, sql, types

from polyfactory.exceptions import ParameterException
from polyfactory.factories.sqlalchemy_factory import SQLAlchemyFactory

if __version__.startswith("1"):
    pytest.importorskip("SQLAlchemy", "2")


class Base(orm.DeclarativeBase):
    ...


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
    class Base(orm.DeclarativeBase):
        ...

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


@pytest.mark.parametrize(
    "type_",
    tuple(SQLAlchemyFactory.get_sqlalchemy_types().keys()),
)
def test_sqlalchemy_type_handlers_v2(type_: types.TypeEngine) -> None:
    class Base(orm.DeclarativeBase):
        ...

    class Model(Base):
        __tablename__ = "model_with_overriden_type"

        id: orm.Mapped[int] = orm.mapped_column(primary_key=True)
        overridden: orm.Mapped[Any] = orm.mapped_column(type_=type_)

    class ModelFactory(SQLAlchemyFactory[Model]):
        __model__ = Model

    instance = ModelFactory.build()
    assert instance.overridden is not None


@pytest.mark.parametrize(
    "impl_",
    (
        sql.sqltypes.BigInteger(),
        sql.sqltypes.Boolean(),
        sql.sqltypes.Date(),
        sql.sqltypes.DateTime(),
        sql.sqltypes.Double(),
        sql.sqltypes.Enum(),
        sql.sqltypes.Float(),
        sql.sqltypes.Integer(),
        sql.sqltypes.Interval(),
        sql.sqltypes.LargeBinary(),
        sql.sqltypes.MatchType(),
        sql.sqltypes.Numeric(),
        sql.sqltypes.SmallInteger(),
        sql.sqltypes.String(),
        sql.sqltypes.Text(),
        sql.sqltypes.Time(),
        sql.sqltypes.Unicode(),  # type: ignore[no-untyped-call]
        sql.sqltypes.UnicodeText(),  # type: ignore[no-untyped-call]
        sql.sqltypes.Uuid(),
    ),
)
def test_sqlalchemy_custom_type_from_type_decorator(impl_: types.TypeEngine) -> None:
    class CustomType(types.TypeDecorator):
        impl = impl_

    class Base(orm.DeclarativeBase):
        type_annotation_map = {object: CustomType}

    class Model(Base):
        __tablename__ = "model_with_custom_types"

        id: orm.Mapped[int] = orm.mapped_column(primary_key=True)
        custom_type: orm.Mapped[Any] = orm.mapped_column(type_=CustomType(), nullable=False)
        custom_type_from_annotation_map: orm.Mapped[object]

    class ModelFactory(SQLAlchemyFactory[Model]):
        __model__ = Model

    instance = ModelFactory.build()
    assert isinstance(instance.id, int)
    assert isinstance(instance.custom_type, impl_.python_type)
    assert isinstance(instance.custom_type_from_annotation_map, impl_.python_type)


def test_sqlalchemy_custom_type_from_user_defined_type__overridden() -> None:
    class CustomType(types.UserDefinedType):
        ...

    class Base(orm.DeclarativeBase):
        ...

    class Model(Base):
        __tablename__ = "model_with_custom_types"

        id: orm.Mapped[int] = orm.mapped_column(primary_key=True)
        custom_type: orm.Mapped[Any] = orm.mapped_column(type_=CustomType())

    class ModelFactory(SQLAlchemyFactory[Model]):
        __model__ = Model

        @classmethod
        def get_sqlalchemy_types(cls) -> dict[Any, Callable[[], Any]]:
            return super().get_sqlalchemy_types() | {CustomType: lambda: cls.__faker__.date_time()}

    instance = ModelFactory.build()
    assert isinstance(instance.id, int)
    assert isinstance(instance.custom_type, datetime.datetime)


def test_sqlalchemy_custom_type_from_user_defined_type__type_not_supported() -> None:
    class CustomType(types.UserDefinedType):
        ...

    class Base(orm.DeclarativeBase):
        ...

    class Model(Base):
        __tablename__ = "model_with_custom_types"

        id: orm.Mapped[int] = orm.mapped_column(primary_key=True)
        custom_type: orm.Mapped[Any] = orm.mapped_column(type_=CustomType())

    class ModelFactory(SQLAlchemyFactory[Model]):
        __model__ = Model

    with pytest.raises(ParameterException, match="User defined type detected"):
        ModelFactory.build()
