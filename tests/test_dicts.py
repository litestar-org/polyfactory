from typing import Dict, Union

import pytest
from pydantic import BaseModel

from polyfactory.factories.pydantic_factory import ModelFactory, pydantic_version


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


@pytest.mark.skipif(
    pydantic_version == 2,
    reason="indeterminate behaviour in pydantic 2.0",
)
def test_dict_with_union_random_types() -> None:
    class MyClass(BaseModel):
        val: Dict[str, Union[int, str]]

    class MyClassFactory(ModelFactory[MyClass]):
        __model__ = MyClass

    MyClassFactory.seed_random(100)

    test_obj_1 = MyClassFactory.build()
    test_obj_2 = MyClassFactory.build()

    assert isinstance(list(test_obj_1.val.values())[0], str)
    assert isinstance(list(test_obj_2.val.values())[0], int)
