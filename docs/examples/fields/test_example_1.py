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


pet_instance = Pet(name="Roxy", sound="woof woof", species=Species.DOG)


class PersonFactory(DataclassFactory[Person]):
    pets = [pet_instance]


def test_is_pet_instance() -> None:
    person_instance = PersonFactory.build()
    assert len(person_instance.pets) == 1
    assert person_instance.pets[0] == pet_instance
