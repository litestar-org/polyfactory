from typing import Annotated

from msgspec import Meta, Struct

from polyfactory.factories.msgspec_factory import MsgspecFactory


class Payment(Struct):
    amount: int
    currency: Annotated[str, Meta(examples=["USD", "EUR", "INR"])]


class PaymentFactory(MsgspecFactory[Payment]):
    __use_examples__ = True


def test_use_examples() -> None:
    instance = PaymentFactory.build()
    assert instance.currency in ["USD", "EUR", "INR"]
