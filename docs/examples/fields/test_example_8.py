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
    pet: Pet
    assets: List[Dict[str, Dict[str, Any]]]


class PetFactory(DataclassFactory[Pet]):
    name = lambda: DataclassFactory.__random__.choice(["Ralph", "Roxy"])


class PersonFactory(DataclassFactory[Person]):
    pet = PetFactory


def test_subfactory() -> None:
    person_instance = PersonFactory.build()

    assert isinstance(person_instance.pet, Pet)
    assert person_instance.pet.name in ["Ralph", "Roxy"]

    person_instance_with_pet_name = PersonFactory.build(pet={"name": "Winston"})
    assert person_instance_with_pet_name.pet.name == "Winston"
