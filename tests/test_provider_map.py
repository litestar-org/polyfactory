from dataclasses import dataclass
from typing import Any, Callable

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
        def get_provider_map(cls) -> dict[Any, Callable[[], Any]]:
            provider_map = super().get_provider_map()
            provider_map[Any] = lambda: "any"

            return provider_map

    foo = FooFactory.build()

    assert foo.foo == "any"
