from dataclasses import dataclass

from polyfactory.factories import DataclassFactory


@dataclass
class Person:
    name: str
    age: float
    height: float
    weight: float


class PersonFactory(DataclassFactory[Person]):
    __model__ = Person


def test_is_person() -> None:
    person_instance = PersonFactory.build()
    assert isinstance(person_instance, Person)
    assert isinstance(person_instance.name, str)
    assert isinstance(person_instance.age, float)
    assert isinstance(person_instance.height, float)
    assert isinstance(person_instance.weight, float)
