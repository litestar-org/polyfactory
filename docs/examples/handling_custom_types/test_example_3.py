from dataclasses import dataclass
from typing import TypeVar
from uuid import UUID

from polyfactory.factories import DataclassFactory
from polyfactory.factories.base import BaseFactory


# we created a special class we will use in our code
class CustomSecret:
    def __init__(self, value: str) -> None:
        self.value = value

    def __repr__(self) -> str:
        return "*" * len(self.value)

    def __str__(self) -> str:
        return "*" * len(self.value)


T = TypeVar("T")


# we add a function to generate the custom type
BaseFactory.add_provider(CustomSecret, lambda: CustomSecret("jeronimo"))


@dataclass
class Person:
    id: UUID
    secret: CustomSecret


# we don't have to use a custom base factory!
class PersonFactory(DataclassFactory[Person]): ...


def test_custom_dataclass_base_factory() -> None:
    person_instance = PersonFactory.build()
    assert isinstance(person_instance.secret, CustomSecret)
    assert repr(person_instance.secret) == "*" * len("jeronimo")
    assert str(person_instance.secret) == "*" * len("jeronimo")
    assert person_instance.secret.value == "jeronimo"
