from dataclasses import dataclass
from typing import Any, Callable, Generic, TypeVar

import pytest

from pydantic import BaseModel

from polyfactory.exceptions import ParameterException
from polyfactory.factories.base import BaseFactory
from polyfactory.factories.dataclass_factory import DataclassFactory
from polyfactory.factories.pydantic_factory import ModelFactory


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
        def get_provider_map(cls) -> dict[Any, Callable[[], Any]]:
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
        def get_provider_map(cls) -> dict[Any, Callable[[], Any]]:
            provider_map = super().get_provider_map()
            provider_map[T] = lambda: "any"

            return provider_map

    foo = FooFactory.build()
    assert foo.foo == "any"

    coverage_result = list(FooFactory.coverage())
    assert all(result.foo == "any" for result in coverage_result)


def test_provider_map_takes_priority_over_factory_type() -> None:
    """Custom providers should take precedence over built-in factory type resolution."""

    @dataclass
    class Inner:
        value: str

    @dataclass
    class Outer:
        inner: Inner

    sentinel = Inner(value="from_provider")

    class OuterFactory(DataclassFactory[Outer]):
        @classmethod
        def get_provider_map(cls) -> dict[Any, Callable[[], Any]]:
            return {Inner: lambda: sentinel, **super().get_provider_map()}

    assert OuterFactory.build().inner is sentinel
    assert all(result.inner is sentinel for result in OuterFactory.coverage())


def test_provider_map_takes_priority_over_pydantic_factory_type() -> None:
    """Custom providers should take precedence for Pydantic model fields."""

    class InnerModel(BaseModel):
        value: str

    class OuterModel(BaseModel):
        inner: InnerModel

    class OuterFactory(ModelFactory[OuterModel]):
        @classmethod
        def get_provider_map(cls) -> dict[Any, Callable[[], Any]]:
            return {InnerModel: lambda: InnerModel(value="from_provider"), **super().get_provider_map()}

    assert OuterFactory.build().inner.value == "from_provider"
    assert all(result.inner.value == "from_provider" for result in OuterFactory.coverage())


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
