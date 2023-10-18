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


@dataclass
class SocialGroup:
    members: list[Profile]


class SocialGroupFactory(DataclassFactory[SocialGroup]):
    __model__ = SocialGroup


group = list(SocialGroupFactory.coverage())

# >>> print(group)
# >>> SocialGroup(members=[Profile(...), Profile(...), Profile(...)])
