from dataclasses import dataclass as vanilla_dataclass
from dataclasses import field
from typing import Dict, List, Optional

from pydantic.dataclasses import Field  # type: ignore
from pydantic.dataclasses import dataclass as pydantic_dataclass

from polyfactory.factories.base import DataclassFactory
from tests.models import Person


def test_factory_vanilla_dc() -> None:
    @vanilla_dataclass
    class VanillaDC:
        id: int
        name: str
        list_field: List[Dict[str, int]]
        field_of_some_value: Optional[int] = field(default_factory=lambda: 0)

    class MyFactory(DataclassFactory[VanillaDC]):
        __model__ = VanillaDC

    result = MyFactory.build()

    assert result
    assert result.id
    assert result.name
    assert result.list_field
    assert result.list_field[0]
    assert [isinstance(value, int) for value in result.list_field[0].values()]


def test_factory_pydantic_dc() -> None:
    @pydantic_dataclass
    class PydanticDC:
        id: int
        name: str
        list_field: List[Dict[str, int]]
        constrained_field: int = Field(ge=100)
        field_of_some_value: Optional[int] = field(default_factory=lambda: 0)

    class MyFactory(DataclassFactory[PydanticDC]):
        __model__ = PydanticDC

    result = MyFactory.build()

    assert result
    assert result.id
    assert result.name
    assert result.list_field
    assert result.list_field[0]
    assert [isinstance(value, int) for value in result.list_field[0].values()]
    assert result.constrained_field >= 100


def test_vanilla_dc_with_embedded_model() -> None:
    @vanilla_dataclass
    class VanillaDC:
        people: List[Person]

    class MyFactory(DataclassFactory[VanillaDC]):
        __model__ = VanillaDC

    result = MyFactory.build()

    assert result.people
    assert [isinstance(person, Person) for person in result.people]


def test_pydantic_dc_with_embedded_model() -> None:
    @vanilla_dataclass
    class PydanticDC:
        people: List[Person]

    class MyFactory(DataclassFactory):
        __model__ = PydanticDC

    result = MyFactory.build()

    assert result.people
    assert [isinstance(person, Person) for person in result.people]


def test_model_with_embedded_dataclasses() -> None:
    @vanilla_dataclass
    class VanillaDC:
        people: List[Person]

    @vanilla_dataclass
    class PydanticDC:
        people: List[Person]

    @vanilla_dataclass
    class Crowd:
        west: VanillaDC
        east: PydanticDC

    class MyFactory(DataclassFactory):
        __model__ = Crowd

    result = MyFactory.build()

    assert result.west
    assert result.west.people
    assert result.east
    assert result.east.people


def function_with_kwargs(first: int, second: float, third: str = "moishe") -> None:
    pass


def test_complex_embedded_dataclass() -> None:
    @vanilla_dataclass
    class VanillaDC:
        people: List[Person]

    @vanilla_dataclass
    class MyModel:
        weirdly_nest_field: List[Dict[str, Dict[str, VanillaDC]]]

    class MyFactory(DataclassFactory):
        __model__ = MyModel

    result = MyFactory.build()

    assert result.weirdly_nest_field
    assert result.weirdly_nest_field[0]
    assert list(result.weirdly_nest_field[0].values())[0].values()
    assert list(list(result.weirdly_nest_field[0].values())[0].values())[0]
    assert isinstance(list(list(result.weirdly_nest_field[0].values())[0].values())[0], VanillaDC)
