from dataclasses import dataclass
from random import Random

from polyfactory.factories import DataclassFactory


@dataclass
class Person:
    name: str
    age: float
    height: float
    weight: float


class PersonFactory(DataclassFactory[Person]):
    __random__ = Random(10)

    @classmethod
    def name(cls) -> str:
        return cls.__random__.choice(["John", "Alice", "George"])


def test_setting_random() -> None:
    # the outcome of 'factory.__random__.choice' is deterministic, because Random is configured with a set value.
    assert PersonFactory.build().name == "George"
    assert PersonFactory.build().name == "John"
    assert PersonFactory.build().name == "Alice"
