from typing import List

from pydantic import BaseModel

from pydantic_factories import ModelFactory


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
    AFactory = ModelFactory.create_factory(model=A, a_text="const value")
    BFactory = ModelFactory.create_factory(model=B, b_text="const value", __auto_register__=True)
    CFactory = ModelFactory.create_factory(model=C)

    c = CFactory.build()

    assert c.b.b_text == BFactory.b_text
    assert c.b_list[0].b_text == BFactory.b_text
    assert c.b.a.a_text != AFactory.a_text
