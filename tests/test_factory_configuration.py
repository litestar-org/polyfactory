from dataclasses import dataclass
from typing import Annotated, Any, Callable

from typing_extensions import TypeGuard

from polyfactory.factories.base import BaseFactory, T
from polyfactory.factories.dataclass_factory import DataclassFactory
from polyfactory.field_meta import FieldMeta


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


def test_inheriting_config() -> None:
    class CustomType:
        def __init__(self, a: int) -> None:
            self.a = a

    @dataclass
    class Child:
        a: list[int]
        custom_type: CustomType

    @dataclass
    class Parent:
        children: list[Child]

    class ParentFactory(DataclassFactory[Parent]):
        __randomize_collection_length__ = True
        __min_collection_length__ = 5
        __max_collection_length__ = 5

        @classmethod
        def get_provider_map(cls) -> dict[Any, Callable[[], Any]]:
            return {
                **super().get_provider_map(),
                int: lambda: 42,
                CustomType: lambda: CustomType(a=5),
            }

    result = ParentFactory.build()
    assert len(result.children) == 5
    assert result.children[0].a == [42] * 5
    assert result.children[0].custom_type.a == 5


def test_use_examples_from_annotation_metadata() -> None:
    class Examples:
        def __init__(self, *examples: Any) -> None:
            self.examples = list(examples)

    @dataclass
    class Payment:
        currency: Annotated[str, Examples("USD", "EUR", "INR")]

    class PaymentFactory(DataclassFactory[Payment]):
        __use_examples__ = True

    assert PaymentFactory.build().currency in ["USD", "EUR", "INR"]


def test_use_examples_with_custom_base_factory() -> None:
    class Payment:
        def __init__(self, currency: str) -> None:
            self.currency = currency

    class PaymentFactory(BaseFactory[Payment]):
        __model__ = Payment
        __use_examples__ = True

        @classmethod
        def is_supported_type(cls, value: Any) -> TypeGuard[type[Payment]]:
            return value is Payment

        @classmethod
        def get_model_fields(cls) -> list[FieldMeta]:
            return [FieldMeta.from_type(str, name="currency", examples=["USD", "EUR", "INR"])]

    assert PaymentFactory.build().currency in ["USD", "EUR", "INR"]
    assert {payment.currency for payment in PaymentFactory.coverage()} == {"USD", "EUR", "INR"}
