from dataclasses import dataclass
from typing import List

from polyfactory.decorators import post_generated
from polyfactory.factories import DataclassFactory
from polyfactory.fields import Param


@dataclass
class Pet:
    name: str
    sound: str


class PetFactoryWithParamValueSetAtBuild(DataclassFactory[Pet]):
    """In this factory, the name_choices must be passed at build time."""

    name_choices = Param[List[str]]()

    @post_generated
    @classmethod
    def name(cls, name_choices: List[str]) -> str:
        return cls.__random__.choice(name_choices)


def test_factory__build_time() -> None:
    names = ["Ralph", "Roxy"]
    pet = PetFactoryWithParamValueSetAtBuild.build(name_choices=names)

    assert isinstance(pet, Pet)
    assert not hasattr(pet, "name_choices")
    assert pet.name in names


class PetFactoryWithParamSpecififiedInFactory(DataclassFactory[Pet]):
    """In this factory, the name_choices are specified in the
    factory and do not need to be passed at build time."""

    name_choices = Param[List[str]](["Ralph", "Roxy"])

    @post_generated
    @classmethod
    def name(cls, name_choices: List[str]) -> str:
        return cls.__random__.choice(name_choices)


def test_factory__in_factory() -> None:
    pet = PetFactoryWithParamSpecififiedInFactory.build()

    assert isinstance(pet, Pet)
    assert not hasattr(pet, "name_choices")
    assert pet.name in ["Ralph", "Roxy"]
