from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional, Union
from uuid import UUID

from polyfactory.factories import DataclassFactory
from polyfactory.pytest_plugin import register_fixture


@dataclass
class Person:
    id: UUID
    name: str
    hobbies: list[str] | None
    nicks: list[str]
    age: float | int
    birthday: datetime | date


@register_fixture
class PersonFactory(DataclassFactory[Person]): ...


def test_person_factory(person_factory: PersonFactory) -> None:
    person_instance = person_factory.build()
    assert isinstance(person_instance, Person)

    # The factory class itself can still be used
    another_person_instance = PersonFactory.build()
    assert isinstance(another_person_instance, Person)
