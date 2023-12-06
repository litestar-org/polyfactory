from typing import Dict, List, Optional

from typing_extensions import TypedDict

from polyfactory.factories import TypedDictFactory


class TypedDictModel(TypedDict):
    id: int
    name: str
    list_field: List[Dict[str, int]]
    int_field: Optional[int]


def test_factory_with_typeddict() -> None:
    class MyFactory(TypedDictFactory[TypedDictModel]):
        ...

    assert getattr(MyFactory, "__model__") is TypedDictModel
    result: TypedDictModel = MyFactory.build()

    assert isinstance(result, dict)
    assert result["id"]
    assert result["name"]
    assert result["list_field"][0]
    assert type(result["int_field"]) in (type(None), int)
