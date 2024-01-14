from dataclasses import dataclass
from enum import Enum

from polyfactory.factories import DataclassFactory


class Species(str, Enum):
    CAT = "Cat"
    DOG = "Dog"


@dataclass
class Pet:
    name: str
    sound: str = "meow"
    species: Species = Species.CAT


class PetFactory(DataclassFactory[Pet]):
    __model__ = Pet
    __use_defaults__ = True


def test_use_default() -> None:
    pet = PetFactory.build()

    assert pet.species == Species.CAT
    assert pet.sound == "meow"
