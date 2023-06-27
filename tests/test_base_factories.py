from dataclasses import dataclass
from typing import Any, Dict

import pytest
from pydantic.main import BaseModel

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

    # noinspection PyUnusedLocal
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

    # noinspection PyUnusedLocal
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

    # XXX: remove the factory classes from _base_factories to prevent side-effects in other tests
    # see https://github.com/litestar-org/polyfactory/issues/198
    ModelFactory._base_factories.remove(FooModelFactory)
    ModelFactory._base_factories.remove(DummyModelFactory)
