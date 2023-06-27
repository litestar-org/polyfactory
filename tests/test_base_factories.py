from dataclasses import dataclass
from typing import Any, Dict

from polyfactory.factories import DataclassFactory


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
        __base_factory_overrides__ = {MyModel: FooDataclassFactory, MyModelWithFoo: FooDataclassFactory}

    MyFactory.build()
