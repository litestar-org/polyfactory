from dataclasses import dataclass
from datetime import date, datetime
from enum import Enum
from typing import Any, Dict, List, Union
from uuid import UUID

from polyfactory import Use
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


class PetFactory(DataclassFactory[Pet]):
    name = lambda: DataclassFactory.__random__.choice(["Ralph", "Roxy"])
    species = lambda: DataclassFactory.__random__.choice(list(Species))


class PersonFactory(DataclassFactory[Person]):
    pets = Use(PetFactory.batch, size=2)


def test_pet_choices() -> None:
    person_instance = PersonFactory.build()

    assert len(person_instance.pets) == 2
    assert all(pet.name in ["Ralph", "Roxy"] for pet in person_instance.pets)
