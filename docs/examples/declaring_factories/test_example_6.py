from dataclasses import dataclass
from enum import Enum

from polyfactory.factories import DataclassFactory


class Species(str, Enum):
    CAT = "Cat"
    DOG = "Dog"


@dataclass
class Pet:
    name: str
    species: Species
    sound: str


def test_imperative_factory_creation() -> None:
    pet_factory = DataclassFactory.create_factory(model=Pet)
    pet_instance = pet_factory.build()
    assert isinstance(pet_instance, Pet)
