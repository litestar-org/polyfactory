from dataclasses import dataclass
from datetime import date, datetime
from enum import Enum
from typing import Any, Union
from uuid import UUID

from polyfactory.factories import DataclassFactory


class Species(str, Enum):
    CAT = "Cat"
    DOG = "Dog"


@dataclass
class Pet:
    name: str
    species: Species
    sound: str


@dataclass
class Person:
    id: UUID
    name: str
    hobbies: list[str]
    age: Union[float, int]
    birthday: Union[datetime, date]
    pets: list[Pet]
    assets: list[dict[str, dict[str, Any]]]


class PersonFactory(DataclassFactory[Person]): ...


def test_dynamic_factory_generation() -> None:
    person_instance = PersonFactory.build()
    assert len(person_instance.pets) > 0
    assert isinstance(person_instance.pets[0], Pet)
