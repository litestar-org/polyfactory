from typing import TypedDict

from polyfactory.factories import TypedDictFactory


class Person(TypedDict):
    name: str
    age: float
    height: float
    weight: float


class PersonFactory(TypedDictFactory[Person]): ...


def test_is_person() -> None:
    person_instance = PersonFactory.build()
    assert isinstance(person_instance, dict)
    assert isinstance(person_instance.get("name"), str)
    assert isinstance(person_instance.get("age"), float)
    assert isinstance(person_instance.get("height"), float)
    assert isinstance(person_instance.get("weight"), float)
