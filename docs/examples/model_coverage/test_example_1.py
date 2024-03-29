from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from polyfactory.factories.dataclass_factory import DataclassFactory


@dataclass
class Car:
    model: str


@dataclass
class Boat:
    can_float: bool


@dataclass
class Profile:
    age: int
    favourite_color: Literal["red", "green", "blue"]
    vehicle: Car | Boat


class ProfileFactory(DataclassFactory[Profile]): ...


def test_profile_coverage() -> None:
    profiles = list(ProfileFactory.coverage())

    assert profiles[0].favourite_color == "red"
    assert isinstance(profiles[0].vehicle, Car)
    assert profiles[1].favourite_color == "green"
    assert isinstance(profiles[1].vehicle, Boat)
    assert profiles[2].favourite_color == "blue"
    assert isinstance(profiles[2].vehicle, Car)
