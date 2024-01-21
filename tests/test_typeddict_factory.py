from typing import Dict, List, Optional

from annotated_types import Ge
from typing_extensions import Annotated, NotRequired, Required, TypedDict

from pydantic import BaseModel

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


def test_typeddict_with_required_and_non_required_fields() -> None:
    class TypedDictModel(TypedDict):
        id: Required[int]
        name: NotRequired[str]
        annotated: Required[Annotated[int, Ge(100)]]
        list_field: List[Dict[str, int]]
        optional_int: Required[Optional[int]]

    class TypedDictModelFactory(TypedDictFactory[TypedDictModel]):
        __model__ = TypedDictModel

    result = TypedDictModelFactory.build()

    assert isinstance(result["id"], int)
    assert isinstance(result["annotated"], int)
    assert result["annotated"] >= 100
    assert isinstance(result["list_field"], list)
    assert isinstance(result["optional_int"], (type(None), int))
    assert "name" in result
    assert isinstance(result["name"], str)
