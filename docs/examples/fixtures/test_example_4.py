from dataclasses import dataclass
from typing import Optional, List, Union
from datetime import datetime, date
from uuid import UUID
from polyfactory import Fixture
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


@dataclass
class ClassRoom:
    teacher: Person
    pupils: List[Person]


@register_fixture
class PersonFactory(DataclassFactory[Person]):
    __model__ = Person


class ClassRoomFactory(DataclassFactory[ClassRoom]):
    __model__ = ClassRoom

    teacher = Fixture(PersonFactory, name="Ludmilla Newman")
    pupils = Fixture(PersonFactory, size=20)


def test_fixture_field() -> None:
    classroom_instance = ClassRoomFactory.build()

    assert isinstance(classroom_instance.teacher, Person)
    assert classroom_instance.teacher.name == "Ludmilla Newman"
    assert len(classroom_instance.pupils) == 20
