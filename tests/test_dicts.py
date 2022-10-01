from typing import Dict

from pydantic import BaseModel

from pydantic_factories import ModelFactory


def test_passing_nested_dict() -> None:
    class MyMappedClass(BaseModel):
        val: str

    class MyClass(BaseModel):
        my_mapping_obj: Dict[str, MyMappedClass]
        my_mapping_str: Dict[str, str]

    class MyClassFactory(ModelFactory[MyClass]):
        __model__ = MyClass

    obj = MyClassFactory.build(
        my_mapping_str={"foo": "bar"},
        my_mapping_obj={"baz": MyMappedClass(val="bar")},
    )

    assert obj.dict() == {"my_mapping_obj": {"baz": {"val": "bar"}}, "my_mapping_str": {"foo": "bar"}}
