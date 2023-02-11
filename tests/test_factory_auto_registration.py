from dataclasses import dataclass as vanilla_dataclass
from typing import List

from pydantic import BaseModel
from typing_extensions import TypedDict

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
        __auto_register__ = True

    class CFactory(ModelFactory):
        __model__ = C

    c = CFactory.build()

    assert c.b.b_text == BFactory.b_text
    assert c.b_list[0].b_text == BFactory.b_text
    assert c.b.a.a_text != AFactory.a_text


def test_auto_register_model_factory_using_create_factory() -> None:
    const_value = "const value"
    ModelFactory.create_factory(model=A, a_text=const_value)
    ModelFactory.create_factory(model=B, b_text=const_value, __auto_register__=True)
    factory = ModelFactory.create_factory(model=C)

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

    class UpperModelFactory(ModelFactory):
        __model__ = UpperModel

    class DataClassFactory(ModelFactory):
        text = "const value"
        __model__ = DataClass
        __auto_register__ = True

    upper = UpperModelFactory.build()

    assert upper.nested_field.text == DataClassFactory.text
    assert upper.nested_list_field[0].text == DataClassFactory.text


def test_typeddict_model_factory_auto_registration() -> None:
    class TypedDictModel(TypedDict):
        text: str

    class UpperSchema(BaseModel):
        nested_field: TypedDictModel
        nested_list_field: List[TypedDictModel]

    class UpperModelFactory(ModelFactory):
        __model__ = UpperSchema

    class TypedDictFactory(ModelFactory):
        text = "const value"
        __model__ = TypedDictModel
        __auto_register__ = True

    upper = UpperModelFactory.build()

    assert upper.nested_field["text"] == TypedDictFactory.text
    assert upper.nested_list_field[0]["text"] == TypedDictFactory.text
