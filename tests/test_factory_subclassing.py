from dataclasses import dataclass

import pytest

from pydantic import BaseModel

from polyfactory import ConfigurationException
from polyfactory.factories import DataclassFactory
from polyfactory.factories.pydantic_factory import ModelFactory
from polyfactory.field_meta import Null


def test_factory_raises_config_error_for_unsupported_model_with_supported_factory() -> None:
    @dataclass
    class DataclassModel:
        id: int

    with pytest.raises(ConfigurationException):

        class MyFactory1(ModelFactory):
            __model__ = DataclassModel

    class MyFactory2(DataclassFactory):
        __model__ = DataclassModel


def test_factory_raises_config_error_for_unsupported_model() -> None:
    with pytest.raises(ConfigurationException, match="Model type Null is not supported"):

        class MyFactory(ModelFactory):
            __model__ = Null


def test_inherit_concrete_factory() -> None:
    class Parent(BaseModel):
        name: str

    class Child(Parent):
        n: int

    class ParentFactory(ModelFactory):
        __model__ = Parent

        @classmethod
        def name(cls) -> str:
            return cls.__model__.__name__

    class ChildFactory(ParentFactory):
        __model__ = Child  # type: ignore[assignment]

    assert ParentFactory.build().name == "Parent"
    assert ChildFactory.build().name == "Child"


def test_inherit_base_factory() -> None:
    class Parent(BaseModel):
        name: str

    class Child(Parent):
        n: int

    class ParentFactory(ModelFactory):
        __is_base_factory__ = True

        @classmethod
        def name(cls) -> str:
            return cls.__model__.__name__

    class ChildFactory(ParentFactory):
        __model__ = Child

    exc_info = pytest.raises(AttributeError, ParentFactory.build)
    assert "'ParentFactory' has no attribute '__model__'" in str(exc_info.value)
    assert ChildFactory.build().name == "Child"

    # remove the ParentFactory from _base_factories to prevent side effects in other tests
    # see https://github.com/litestar-org/polyfactory/issues/198
    ModelFactory._base_factories.remove(ParentFactory)
