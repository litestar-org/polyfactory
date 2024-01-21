from typing import Dict, Union

import pytest

from pydantic import VERSION, BaseModel

from polyfactory.factories.pydantic_factory import ModelFactory


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
    VERSION.startswith("2"),
    reason="indeterminate behaviour in pydantic 2.0",
)
def test_dict_with_union_random_types() -> None:
    class MyClass(BaseModel):
        val: Dict[str, Union[int, str]]

    class MyClassFactory(ModelFactory[MyClass]):
        __model__ = MyClass

    MyClassFactory.seed_random(10)

    test_obj_1 = MyClassFactory.build()
    test_obj_2 = MyClassFactory.build()

    assert isinstance(next(iter(test_obj_1.val.values())), str)
    assert isinstance(next(iter(test_obj_2.val.values())), int)
