from typing import Generic, TypeVar

from pydantic.generics import GenericModel

from polyfactory.factories.pydantic_factory import ModelFactory


def test_generic_model_is_not_an_error() -> None:
    T = TypeVar("T")
    P = TypeVar("P")

    class Foo(GenericModel, Generic[T, P]):  # type: ignore[misc]
        val1: T
        val2: P

    class FooFactory(ModelFactory[Foo[str, int]]):
        ...

    assert isinstance(FooFactory.build().val1, str)
    assert isinstance(FooFactory.build().val2, int)
