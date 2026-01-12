from dataclasses import dataclass
from uuid import UUID

from polyfactory.factories.dataclass_factory import DataclassFactory


@dataclass
class Person:
    id: UUID
    name: str | None


class PersonFactory(DataclassFactory[Person]):
    __allow_none_optionals__ = False


def test_optional_type_ignored() -> None:
    person_instance = PersonFactory.build()
    assert isinstance(person_instance.name, str)
