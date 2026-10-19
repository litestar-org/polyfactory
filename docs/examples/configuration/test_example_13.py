from typing import Annotated

from msgspec import Meta, Struct

from polyfactory.factories.msgspec_factory import MsgspecFactory

_SUPPORTED_CURRENCIES = ["USD", "EUR", "INR"]


class Payment(Struct):
    amount: int
    currency: Annotated[str, Meta(examples=_SUPPORTED_CURRENCIES)]


class PaymentFactory(MsgspecFactory[Payment]):
    __use_examples__ = True


def test_use_examples() -> None:
    instance = PaymentFactory.build()
    assert instance.currency in _SUPPORTED_CURRENCIES
