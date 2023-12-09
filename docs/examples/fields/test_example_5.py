from typing import TypedDict

from polyfactory import Ignore
from polyfactory.factories import TypedDictFactory


class Person(TypedDict):
    id: int
    name: str


class PersonFactory(TypedDictFactory[Person]):
    id = Ignore()


def test_id_is_ignored() -> None:
    person_instance = PersonFactory.build()

    assert person_instance.get("name")
    assert person_instance.get("id") is None
