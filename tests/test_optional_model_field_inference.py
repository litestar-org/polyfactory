from typing import Any, Dict, Generic, Type, TypedDict, TypeVar

import pytest
from attrs import define
from msgspec import Struct
from sqlalchemy import Column, Integer
from sqlalchemy.orm.decl_api import DeclarativeMeta, registry

from pydantic import BaseModel
from pydantic.generics import GenericModel

from polyfactory import ConfigurationException
from polyfactory.factories import TypedDictFactory
from polyfactory.factories.attrs_factory import AttrsFactory
from polyfactory.factories.base import BaseFactory
from polyfactory.factories.msgspec_factory import MsgspecFactory
from polyfactory.factories.pydantic_factory import ModelFactory
from polyfactory.factories.sqlalchemy_factory import SQLAlchemyFactory

try:
    from odmantic import Model

    from polyfactory.factories.odmantic_odm_factory import OdmanticModelFactory
except ImportError:
    Model, OdmanticModelFactory = None, None  # type: ignore

try:
    from beanie import Document

    from polyfactory.factories.beanie_odm_factory import BeanieDocumentFactory
except ImportError:
    BeanieDocumentFactory = None  # type: ignore
    Document = None  # type: ignore


@define
class AttrsBase:
    bool_field: bool


class ModelBase(BaseModel):
    dict_field: Dict[str, int]


class MsgspecBase(Struct):
    int_field: int


class Base(metaclass=DeclarativeMeta):
    __abstract__ = True

    registry = registry()


class SQLAlchemyBase(Base):
    __tablename__ = "model"

    id: Any = Column(Integer(), primary_key=True)


class TypedDictBase(TypedDict):
    name: str


@pytest.mark.parametrize(
    "base_factory, generic_arg",
    [
        (AttrsFactory, AttrsBase),
        (ModelFactory, ModelBase),
        (MsgspecFactory, MsgspecBase),
        (SQLAlchemyFactory, SQLAlchemyBase),
        (TypedDictFactory, TypedDictBase),
    ],
)
def test_modeL_inference_ok(base_factory: Type[BaseFactory], generic_arg: Type[Any]) -> None:
    class Foo(base_factory[generic_arg]):  # type: ignore
        ...

    assert getattr(Foo, "__model__") is generic_arg


@pytest.mark.skipif(Model is None, reason="Odmantic import error")
def test_odmantic_model_inference_ok() -> None:
    class OdmanticModelBase(Model):  # type: ignore
        name: str

    class Foo(OdmanticModelFactory[OdmanticModelBase]): ...

    assert getattr(Foo, "__model__") is OdmanticModelBase


@pytest.mark.skipif(Document is None, reason="Beanie import error")
def test_beanie_model_inference_ok() -> None:
    class BeanieBase(Document):
        name: str

    class Foo(BeanieDocumentFactory[BeanieBase]): ...

    assert getattr(Foo, "__model__") is BeanieBase


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


def test_generic_model_is_not_an_error() -> None:
    T = TypeVar("T")
    P = TypeVar("P")

    class Foo(GenericModel, Generic[T, P]):  # type: ignore[misc]
        val1: T
        val2: P

    class FooFactory(ModelFactory[Foo[str, int]]): ...

    assert getattr(FooFactory, "__model__") is Foo[str, int]
