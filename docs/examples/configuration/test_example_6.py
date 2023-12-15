from dataclasses import dataclass
from typing import Tuple

from polyfactory.factories import DataclassFactory


@dataclass
class Owner:
    cars: Tuple[str, ...]


class OwnerFactory(DataclassFactory[Owner]):
    __randomize_collection_length__ = True
    __min_collection_length__ = 2
    __max_collection_length__ = 5


def test_randomized_collection_length() -> None:
    owner = OwnerFactory.build()
    assert 2 <= len(owner.cars) <= 5
