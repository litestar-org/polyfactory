from typing import Dict, List, Optional

from pydantic import BaseModel
from typing_extensions import TypedDict

from polyfactory.factories import TypedDictFactory
from polyfactory.factories.pydantic_factory import ModelFactory


class TypedDictModel(TypedDict):
    id: int
    name: str
    list_field: List[Dict[str, int]]
    int_field: Optional[int]


def test_factory_with_typeddict() -> None:
    class MyFactory(TypedDictFactory[TypedDictModel]):
        __model__ = TypedDictModel

    result = MyFactory.build()

    assert isinstance(result, dict)
    assert result["id"]
    assert result["name"]
    assert result["list_field"][0]
    assert type(result["int_field"]) in (type(None), int)


def test_factory_model_with_typeddict_attribute_value() -> None:
    class MyModel(BaseModel):
        td: TypedDictModel
        name: str
        list_field: List[Dict[str, int]]
        int_field: Optional[int]

    class MyFactory(ModelFactory[MyModel]):
        __model__ = MyModel

    result = MyFactory.build()

    assert isinstance(result.td, dict)
    assert result.td["id"]
    assert result.td["name"]
    assert result.td["list_field"][0]
    assert type(result.td["int_field"]) in (type(None), int)
