from dataclasses import dataclass
from typing import Any, Dict, Generic, Type, TypeVar
from uuid import UUID

from polyfactory.factories import DataclassFactory


# we created a special class we will use in our code
class CustomSecret:
    def __init__(self, value: str) -> None:
        self.value = value

    def __repr__(self) -> str:
        return "*" * len(self.value)

    def __str__(self) -> str:
        return "*" * len(self.value)


T = TypeVar("T")


# we create a custom base factory to handle dataclasses, with an extended provider map
class CustomDataclassFactory(Generic[T], DataclassFactory[T]):
    __is_base_factory__ = True

    @classmethod
    def get_provider_map(cls) -> Dict[Type, Any]:
        providers_map = super().get_provider_map()

        return {
            CustomSecret: lambda: CustomSecret("jeronimo"),
            **providers_map,
        }


@dataclass
class Person:
    id: UUID
    secret: CustomSecret


# we use our CustomDataclassFactory as a base for the PersonFactory
class PersonFactory(CustomDataclassFactory[Person]): ...


def test_custom_dataclass_base_factory() -> None:
    person_instance = PersonFactory.build()
    assert isinstance(person_instance.secret, CustomSecret)
    assert repr(person_instance.secret) == "*" * len("jeronimo")
    assert str(person_instance.secret) == "*" * len("jeronimo")
    assert person_instance.secret.value == "jeronimo"
