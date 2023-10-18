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


class ProfileFactory(DataclassFactory[Profile]):
    __model__ = Profile


profiles = list(ProfileFactory.coverage())

# >>> print(profiles)
[
    Profile(
        age=9325,
        favourite_color="red",
        vehicle=Car(model="hrxarraoDbdkBnpxMEiG"),
    ),
    Profile(
        age=6840,
        favourite_color="green",
        vehicle=Boat(can_float=False),
    ),
    Profile(
        age=4769,
        favourite_color="blue",
        vehicle=Car(model="hrxarraoDbdkBnpxMEiG"),
    ),
]
