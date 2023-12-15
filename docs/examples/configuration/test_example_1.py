from dataclasses import dataclass

from polyfactory.factories import DataclassFactory


@dataclass
class Person:
    name: str
    age: float
    height: float
    weight: float


class PersonFactory(DataclassFactory[Person]):
    __random_seed__ = 1

    @classmethod
    def name(cls) -> str:
        return cls.__random__.choice(["John", "Alice", "George"])


def test_random_seed() -> None:
    # the outcome of 'factory.__random__.choice' is deterministic, because Random has been seeded with a set value.
    assert PersonFactory.build().name == "John"
    assert PersonFactory.build().name == "George"
    assert PersonFactory.build().name == "John"
