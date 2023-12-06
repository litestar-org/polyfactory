from enum import Enum
from typing import Any

from sqlalchemy import Column, Integer, String, types
from sqlalchemy.orm.decl_api import DeclarativeMeta, registry

from polyfactory.factories.sqlalchemy_factory import SQLAlchemyFactory


def test_python_type_handling() -> None:
    _registry = registry()

    class Base(metaclass=DeclarativeMeta):
        __abstract__ = True

        registry = _registry
        metadata = _registry.metadata

    class Animal(str, Enum):
        DOG = "Dog"
        CAT = "Cat"

    class Model(Base):
        __tablename__ = "model"

        id: Any = Column(Integer(), primary_key=True)
        str_type: Any = Column(String(), nullable=False)
        enum_type: Any = Column(types.Enum(Animal), nullable=False)
        str_array_type: Any = Column(
            types.ARRAY(types.String),
            nullable=False,
        )

    class ModelFactory(SQLAlchemyFactory[Model]):
        ...

    assert getattr(ModelFactory, "__model__") is Model

    instance: Model = ModelFactory.build()
    assert isinstance(instance.id, int)
    assert isinstance(instance.str_type, str)
    assert isinstance(instance.enum_type, Animal)
    assert isinstance(instance.str_array_type, list)
    assert isinstance(instance.str_array_type[0], str)
