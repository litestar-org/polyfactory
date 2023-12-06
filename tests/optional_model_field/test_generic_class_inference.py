from typing import Generic, TypeVar

from pydantic import BaseModel

from polyfactory.factories.pydantic_factory import ModelFactory


def test_generic_model_is_not_an_error() -> None:
    T = TypeVar("T")

    class Foo(BaseModel, Generic[T]):
        val: T

    class FooFactory(ModelFactory[Foo[str]]):
        ...

    assert isinstance(FooFactory.build().val, str)
