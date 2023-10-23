from dataclasses import dataclass
from enum import Enum

from polyfactory.factories import DataclassFactory


class Species(str, Enum):
    CAT = "Cat"
    DOG = "Dog"
    RABBIT = "Rabbit"
    MOUSE = "Mouse"


@dataclass
class Pet:
    name: str
    species: Species
    sound: str


def test_imperative_sub_factory_creation() -> None:
    pet_factory = DataclassFactory.create_factory(model=Pet)
    cat_factory = pet_factory.create_factory(species=Species.CAT)
    cat_instance = cat_factory.build()

    assert isinstance(cat_instance, Pet)
    assert cat_instance.species == Species.CAT
