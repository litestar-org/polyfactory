from dataclasses import dataclass
from datetime import date, datetime
from enum import Enum
from typing import Any, Dict, List, Union
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
    hobbies: List[str]
    age: Union[float, int]
    birthday: Union[datetime, date]
    pets: List[Pet]
    assets: List[Dict[str, Dict[str, Any]]]


class PersonFactory(DataclassFactory[Person]): ...


def test_dynamic_factory_generation() -> None:
    person_instance = PersonFactory.build()
    assert len(person_instance.pets) > 0
    assert isinstance(person_instance.pets[0], Pet)
