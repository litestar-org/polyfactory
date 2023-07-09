import pytest
from pydantic import VERSION, BaseModel, Field

from polyfactory.factories.pydantic_factory import ModelFactory


@pytest.mark.skipif(VERSION.startswith("2"), reason="pydantic v1 only functionality")
def test_const() -> None:
    class A(BaseModel):
        v: int = Field(1, const=True)

    class AFactory(ModelFactory[A]):
        __model__ = A

    for _ in range(5):
        assert AFactory.build()
