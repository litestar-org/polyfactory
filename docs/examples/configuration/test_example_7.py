from dataclasses import dataclass
from typing import Optional
from uuid import UUID

from polyfactory.factories.dataclass_factory import DataclassFactory


@dataclass
class Person:
    id: UUID
    name: Optional[str]


class PersonFactory(DataclassFactory[Person]):
    __model__ = Person
    __allow_none_optionals__ = True
    __random_seed__ = 0


def test_optional_field() -> None:
    person_instance = PersonFactory.build()
    assert person_instance.name is None
