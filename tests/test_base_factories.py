from dataclasses import dataclass
from typing import Any, Dict

import pytest
from pydantic.main import BaseModel

from polyfactory.exceptions import ParameterException
from polyfactory.factories import DataclassFactory
from polyfactory.factories.pydantic_factory import ModelFactory


def test_multiple_base_factories() -> None:
    class Foo:
        def __init__(self, value: str) -> None:
            self.value = value

    @dataclass
    class MyModelWithFoo:
        foo: Foo

    class FooDataclassFactory(DataclassFactory):
        __is_base_factory__ = True

        @classmethod
        def get_provider_map(cls) -> Dict[Any, Any]:
            return {Foo: lambda: Foo("foo"), **super().get_provider_map()}

    class DummyDataclassFactory(DataclassFactory):
        __is_base_factory__ = True

    @dataclass
    class MyModel:
        nested: MyModelWithFoo

    class MyFactory(FooDataclassFactory):
        __model__ = MyModel
        __base_factory_overrides__ = {MyModelWithFoo: FooDataclassFactory}

    MyFactory.build()


@pytest.mark.parametrize("override_BaseModel", [False, True])
def test_multiple_base_pydantic_factories(override_BaseModel: bool) -> None:
    class Foo:
        def __init__(self, value: str) -> None:
            self.value = value

    class MyModelWithFoo(BaseModel):
        foo: Foo

        class Config:
            arbitrary_types_allowed = True

    class FooModelFactory(ModelFactory):
        __is_base_factory__ = True

        @classmethod
        def get_provider_map(cls) -> Dict[Any, Any]:
            return {Foo: lambda: Foo("foo"), **super().get_provider_map()}

    class DummyModelFactory(ModelFactory):
        __is_base_factory__ = True

    class MyModel(BaseModel):
        nested: MyModelWithFoo

    class MyFactory(FooModelFactory):
        __model__ = MyModel
        if override_BaseModel:
            __base_factory_overrides__ = {BaseModel: FooModelFactory}
        else:
            __base_factory_overrides__ = {MyModelWithFoo: FooModelFactory}

    MyFactory.build()


def test_using_base_factories() -> None:
    class Foo:
        def __init__(self, value: str) -> None:
            self.value = value

    class FooDataclassFactory(DataclassFactory):
        __is_base_factory__ = True

        @classmethod
        def get_provider_map(cls) -> Dict[Any, Any]:
            return {Foo: lambda: Foo("foo"), **super().get_provider_map()}

    @dataclass
    class MyModelWithFoo:
        foo: Foo

    @dataclass
    class MyModel:
        nested: MyModelWithFoo

    class MyFactory(DataclassFactory):
        __model__ = MyModel

    exc_info = pytest.raises(ParameterException, MyFactory.build)
    assert str(exc_info.value).startswith("Unsupported type:")

    with MyFactory.using_base_factories(FooDataclassFactory):
        MyFactory.build()

    exc_info = pytest.raises(ParameterException, MyFactory.build)
    assert str(exc_info.value).startswith("Unsupported type:")
