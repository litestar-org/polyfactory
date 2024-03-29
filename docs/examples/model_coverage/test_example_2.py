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


class SocialGroupFactory(DataclassFactory[SocialGroup]): ...


def test_social_group_coverage() -> None:
    groups = list(SocialGroupFactory.coverage())
    assert len(groups) == 3

    for group in groups:
        assert len(group.members) == 1

    assert groups[0].members[0].favourite_color == "red"
    assert isinstance(groups[0].members[0].vehicle, Car)
    assert groups[1].members[0].favourite_color == "green"
    assert isinstance(groups[1].members[0].vehicle, Boat)
    assert groups[2].members[0].favourite_color == "blue"
    assert isinstance(groups[2].members[0].vehicle, Car)
