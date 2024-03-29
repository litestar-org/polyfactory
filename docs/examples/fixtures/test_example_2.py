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


class PersonFactory(DataclassFactory[Person]): ...


person_factory_fixture = register_fixture(PersonFactory)


def test_person_factory(person_factory: PersonFactory) -> None:
    person_instance = person_factory.build()
    assert isinstance(person_instance, Person)

    # we can still access the factory class itself-
    another_person_instance = PersonFactory.build()
    assert isinstance(another_person_instance, Person)
