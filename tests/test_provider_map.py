from typing import Any

from polyfactory.factories.base import BaseFactory
from polyfactory.factories.base import _create_pydantic_type_map


def test_provider_map() -> None:
    provider_map = BaseFactory.get_provider_map()
    provider_map.pop(Any)
    for key in _create_pydantic_type_map(BaseFactory):  # type: ignore[type-abstract]
        provider_map.pop(key)

    for type_, handler in provider_map.items():
        value = handler()
        assert isinstance(value, type_)
