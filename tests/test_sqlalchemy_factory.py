from dataclasses import dataclass
from enum import Enum
from typing import Optional

import pytest
from sqlalchemy import orm
from sqlalchemy.dialects import mysql
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


def test_type_handling() -> None:
    class Base(orm.DeclarativeBase):
        ...

    class Animal(str, Enum):
        DOG = "Dog"
        CAT = "Cat"

    class Model(Base):
        __tablename__ = "model"

        id: orm.Mapped[int] = mapped_column(primary_key=True)
        provided_type: orm.Mapped[str] = mapped_column(nullable=False)
        overriden_type: orm.Mapped[int] = mapped_column(type_=mysql.YEAR, nullable=False, primary_key=True)
        enum_type: orm.Mapped[Animal]

    class ModelFactory(SQLAlchemyFactory[Model]):
        __model__ = Model

    instance = ModelFactory.build()
    assert isinstance(instance.id, int)
    assert isinstance(instance.provided_type, str)
    assert isinstance(instance.overriden_type, int)
    assert 1901 <= instance.overriden_type <= 2155
    assert isinstance(instance.enum_type, Animal)


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
