from datetime import date, datetime
from typing import Any, Union
from uuid import UUID

import attrs

from polyfactory.factories.attrs_factory import AttrsFactory


@attrs.define
class Person:
    id: UUID
    name: str
    hobbies: list[str]
    age: Union[float, int]
    # an aliased variable
    birthday: Union[datetime, date] = attrs.field(alias="date_of_birth")
    # a "private" variable
    _assets: list[dict[str, dict[str, Any]]]


class PersonFactory(AttrsFactory[Person]): ...


def test_person_factory() -> None:
    person = PersonFactory.build()

    assert isinstance(person, Person)
