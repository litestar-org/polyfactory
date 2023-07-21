from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Tuple

from annotated_types import Ge, Le, LowerCase, UpperCase
from pydantic import BaseModel, Field
from typing_extensions import Annotated

from polyfactory.factories import DataclassFactory
from polyfactory.factories.pydantic_factory import ModelFactory


def test_discriminated_unions() -> None:
    class BasePet(BaseModel):
        name: str

    class BlackCat(BasePet):
        pet_type: Literal["cat"]
        color: Literal["black"]

    class WhiteCat(BasePet):
        pet_type: Literal["cat"]
        color: Literal["white"]

    class Dog(BasePet):
        pet_type: Literal["dog"]

    class Owner(BaseModel):
        pet: Annotated[
            Annotated[BlackCat | WhiteCat, Field(discriminator="color")] | Dog,
            Field(discriminator="pet_type"),
        ]
        name: str

    class OwnerFactory(ModelFactory):
        __model__ = Owner

    assert OwnerFactory.build()


def test_predicated_fields() -> None:
    @dataclass
    class PredicatedMusician:
        name: Annotated[str, UpperCase]
        band: Annotated[str, LowerCase]

    class PredicatedMusicianFactory(DataclassFactory):
        __model__ = PredicatedMusician

    assert PredicatedMusicianFactory.build()


def test_tuple_with_annotated_constraints() -> None:
    class Location(BaseModel):
        long_lat: tuple[Annotated[float, Ge(-180), Le(180)], Annotated[float, Ge(-90), Le(90)]]

    class LocationFactory(ModelFactory[Location]):
        __model__ = Location

    assert LocationFactory.build()


def test_legacy_tuple_with_annotated_constraints() -> None:
    class Location(BaseModel):
        long_lat: Tuple[Annotated[float, Ge(-180), Le(180)], Annotated[float, Ge(-90), Le(90)]]  # noqa

    class LocationFactory(ModelFactory[Location]):
        __model__ = Location

    assert LocationFactory.build()
