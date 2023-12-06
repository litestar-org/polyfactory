from typing import Type, TypedDict

import pytest
from pydantic import BaseModel

from polyfactory import ConfigurationException
from polyfactory.factories import TypedDictFactory
from polyfactory.factories.attrs_factory import AttrsFactory
from polyfactory.factories.base import BaseFactory
from polyfactory.factories.msgspec_factory import MsgspecFactory
from polyfactory.factories.pydantic_factory import ModelFactory
from polyfactory.factories.sqlalchemy_factory import SQLAlchemyFactory


@pytest.mark.parametrize(
    "base_factory",
    [
        AttrsFactory,
        ModelFactory,
        MsgspecFactory,
        SQLAlchemyFactory,
        TypedDictFactory,
    ],
)
def test_model_without_generic_type_inference_error(base_factory: Type[BaseFactory]) -> None:
    with pytest.raises(ConfigurationException):

        class Foo(base_factory):  # type: ignore
            ...


@pytest.mark.parametrize(
    "base_factory",
    [
        AttrsFactory,
        ModelFactory,
        MsgspecFactory,
        SQLAlchemyFactory,
        TypedDictFactory,
    ],
)
def test_model_type_error(base_factory: Type[BaseFactory]) -> None:
    with pytest.raises(ConfigurationException):

        class Foo(base_factory[int]):  # type: ignore
            ...


def test_model_multiple_inheritance_cannot_infer_error() -> None:
    class PFoo(BaseModel):
        val: int

    class TDFoo(TypedDict):
        val: str

    with pytest.raises(ConfigurationException):

        class Foo(ModelFactory[PFoo], TypedDictFactory[TDFoo]):  # type: ignore
            ...
