from dataclasses import dataclass as vanilla_dataclass
from typing import List

from pydantic import BaseModel
from typing_extensions import TypedDict

from polyfactory.factories import DataclassFactory, TypedDictFactory
from polyfactory.factories.pydantic_factory import ModelFactory


class A(BaseModel):
    a_text: str


class B(BaseModel):
    b_text: str
    a: A


class C(BaseModel):
    b: B
    b_list: List[B]


def test_auto_register_model_factory() -> None:
    class AFactory(ModelFactory):
        a_text = "const value"
        __model__ = A

    class BFactory(ModelFactory):
        b_text = "const value"
        __model__ = B

    class CFactory(ModelFactory):
        __model__ = C
        __base_factory_overrides__ = {B: BFactory}

    c = CFactory.build()

    assert c.b.b_text == BFactory.b_text
    assert c.b_list[0].b_text == BFactory.b_text
    assert c.b.a.a_text != AFactory.a_text


def test_auto_register_model_factory_using_create_factory() -> None:
    const_value = "const value"
    ModelFactory.create_factory(model=A, a_text=const_value)
    BFactory = ModelFactory.create_factory(model=B, b_text=const_value)
    factory = ModelFactory.create_factory(model=C, __base_factory_overrides__={B: BFactory})

    c = factory.build()

    assert c.b.b_text == const_value
    assert c.b_list[0].b_text == const_value
    assert c.b.a.a_text != const_value


def test_dataclass_model_factory_auto_registration() -> None:
    @vanilla_dataclass
    class DataClass:
        text: str

    class UpperModel(BaseModel):
        nested_field: DataClass
        nested_list_field: List[DataClass]

    class DTFactory(DataclassFactory):
        text = "const value"
        __model__ = DataClass

    class UpperModelFactory(ModelFactory):
        __model__ = UpperModel
        __base_factory_overrides__ = {DataClass: DTFactory}

    upper = UpperModelFactory.build()

    assert upper.nested_field.text == DTFactory.text
    assert upper.nested_list_field[0].text == DTFactory.text


def test_typeddict_model_factory_auto_registration() -> None:
    class TD(TypedDict):
        text: str

    class UpperSchema(BaseModel):
        nested_field: TD
        nested_list_field: List[TD]

    class TDFactory(TypedDictFactory):
        text = "const value"
        __model__ = TD

    class UpperModelFactory(ModelFactory):
        __model__ = UpperSchema
        __base_factory_overrides__ = {TD: TDFactory}

    upper = UpperModelFactory.build()

    assert upper.nested_field["text"] == TDFactory.text
    assert upper.nested_list_field[0]["text"] == TDFactory.text
