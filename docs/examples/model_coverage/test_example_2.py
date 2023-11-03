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


def test_social_group_coverage() -> None:
    groups = list(SocialGroupFactory.coverage())
    assert len(groups) == 1

    members = groups[0].members
    assert len(members) == 3

    assert members[0].favourite_color == "red"
    assert isinstance(members[0].vehicle, Car)
    assert members[1].favourite_color == "green"
    assert isinstance(members[1].vehicle, Boat)
    assert members[2].favourite_color == "blue"
    assert isinstance(members[2].vehicle, Car)
