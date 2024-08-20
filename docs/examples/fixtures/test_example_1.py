from dataclasses import dataclass
from datetime import date, datetime
from typing import List, Optional, Union
from uuid import UUID

from polyfactory.factories import DataclassFactory
from polyfactory.pytest_plugin import register_fixture


@dataclass
class Person:
    id: UUID
    name: str
    hobbies: Optional[List[str]]
    nicks: List[str]
    age: Union[float, int]
    birthday: Union[datetime, date]


@register_fixture
class PersonFactory(DataclassFactory[Person]): ...


# NOTE: PersonFactory is no more a factory class, it is a callable that returns the decorated factory


def test_person_factory(person_factory: DataclassFactory[Person]) -> None:
    person_instance = person_factory.build()
    assert isinstance(person_instance, Person)
