from pydantic import BaseModel, Field

from polyfactory.factories.pydantic_factory import ModelFactory


class Payment(BaseModel):
    amount: int = Field(0)
    currency: str = Field(examples=["USD", "EUR", "INR"])


class PaymentFactory(ModelFactory[Payment]):
    __use_examples__ = True


def test_use_examples() -> None:
    instance = PaymentFactory.build()
    assert instance.currency in ["USD", "EUR", "INR"]
