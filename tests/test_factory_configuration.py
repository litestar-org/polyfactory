from typing import Any

from typing_extensions import TypeGuard

from polyfactory.factories.base import BaseFactory, T


def test_setting_set_as_default_factory_for_type_on_base_factory() -> None:
    """Setting the value to `True` shouldn't raise exception when initializing."""

    class CustomBaseFactory(BaseFactory[T]):
        __is_base_factory__ = True
        __set_as_default_factory_for_type__ = True

        @classmethod
        def is_supported_type(cls, value: Any) -> TypeGuard[type[T]]:
            # Set this as false since this factory will be injected into the
            # list of base factories, but this obviously shouldn't be ran
            # for any of the types.
            return False
