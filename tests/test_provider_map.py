from dataclasses import dataclass
from typing import Any, Callable, Dict, Generic, TypeVar

import pytest

from polyfactory.exceptions import ParameterException
from polyfactory.factories.base import BaseFactory
from polyfactory.factories.dataclass_factory import DataclassFactory


def test_provider_map() -> None:
    provider_map = BaseFactory.get_provider_map()
    provider_map.pop(Any)

    for type_, handler in provider_map.items():
        value = handler()
        assert isinstance(value, type_)


def test_provider_map_with_any() -> None:
    @dataclass
    class Foo:
        foo: Any

    class FooFactory(DataclassFactory[Foo]):
        @classmethod
        def get_provider_map(cls) -> Dict[Any, Callable[[], Any]]:
            provider_map = super().get_provider_map()
            provider_map[Any] = lambda: "any"

            return provider_map

    foo = FooFactory.build()

    assert foo.foo == "any"

    coverage_result = list(FooFactory.coverage())
    assert all(result.foo == "any" for result in coverage_result)


def test_provider_map_with_typevar() -> None:
    T = TypeVar("T")

    @dataclass
    class Foo(Generic[T]):
        foo: T

    class FooFactory(DataclassFactory[Foo]):
        @classmethod
        def get_provider_map(cls) -> Dict[Any, Callable[[], Any]]:
            provider_map = super().get_provider_map()
            provider_map[T] = lambda: "any"

            return provider_map

    foo = FooFactory.build()
    assert foo.foo == "any"

    coverage_result = list(FooFactory.coverage())
    assert all(result.foo == "any" for result in coverage_result)


def test_add_custom_provider() -> None:
    class CustomType:
        def __init__(self, _: Any) -> None:
            pass

    @dataclass
    class Foo:
        foo: CustomType

    FooFactory = DataclassFactory.create_factory(Foo)

    with pytest.raises(ParameterException):
        FooFactory.build()

    BaseFactory.add_provider(CustomType, lambda: CustomType("custom"))

    # after adding the provider, nothing should raise!
    assert FooFactory.build()
