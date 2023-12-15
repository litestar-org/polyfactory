from typing import TypedDict

import pytest

from polyfactory import Require
from polyfactory.exceptions import MissingBuildKwargException
from polyfactory.factories import TypedDictFactory


class Person(TypedDict):
    id: int
    name: str


class PersonFactory(TypedDictFactory[Person]):
    id = Require()


def test_id_is_required() -> None:
    # this will not raise an exception
    person_instance = PersonFactory.build(id=1)

    assert person_instance.get("name")
    assert person_instance.get("id") == 1

    # but when no kwarg is passed, an exception will be raised:
    with pytest.raises(MissingBuildKwargException):
        PersonFactory.build()
