from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Type

from typing_extensions import TypeGuard

from polyfactory.factories.base import BaseFactory, T
from polyfactory.factories.dataclass_factory import DataclassFactory


def test_setting_set_as_default_factory_for_type_on_base_factory() -> None:
    """Setting the value to `True` shouldn't raise exception when initializing."""

    class CustomBaseFactory(BaseFactory[T]):
        __is_base_factory__ = True
        __set_as_default_factory_for_type__ = True

        @classmethod
        def is_supported_type(cls, value: Any) -> TypeGuard[Type[T]]:
            # Set this as false since this factory will be injected into the
            # list of base factories, but this obviously shouldn't be ran
            # for any of the types.
            return False


def test_inheriting_config() -> None:
    class CustomType:
        def __init__(self, a: int) -> None:
            self.a = a

    @dataclass
    class Child:
        a: List[int]
        custom_type: CustomType

    @dataclass
    class Parent:
        children: List[Child]

    class ParentFactory(DataclassFactory[Parent]):
        __randomize_collection_length__ = True
        __min_collection_length__ = 5
        __max_collection_length__ = 5

        @classmethod
        def get_provider_map(cls) -> Dict[Any, Callable[[], Any]]:
            return {
                **super().get_provider_map(),
                int: lambda: 42,
                CustomType: lambda: CustomType(a=5),
            }

    result = ParentFactory.build()
    assert len(result.children) == 5
    assert result.children[0].a == [42] * 5
    assert result.children[0].custom_type.a == 5
