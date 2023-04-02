from dataclasses import dataclass
from typing import Optional, List, Union
from datetime import datetime, date
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


class PersonFactory(DataclassFactory[Person]):
    __model__ = Person


person_factory_fixture = register_fixture(PersonFactory, name="aliased_person_factory")


def test_person_factory(aliased_person_factory: PersonFactory) -> None:
    person_instance = aliased_person_factory.build()
    assert isinstance(person_instance, Person)
