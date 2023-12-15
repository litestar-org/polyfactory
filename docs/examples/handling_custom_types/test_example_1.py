from dataclasses import dataclass
from typing import Any, Dict, Type
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


@dataclass
class Person:
    id: UUID
    secret: CustomSecret


# by default the factory class cannot handle unknown types,
# so we need to override the provider map to add it:
class PersonFactory(DataclassFactory[Person]):
    @classmethod
    def get_provider_map(cls) -> Dict[Type, Any]:
        providers_map = super().get_provider_map()

        return {
            CustomSecret: lambda: CustomSecret("jeronimo"),
            **providers_map,
        }


def test_custom_secret_creation() -> None:
    person_instance = PersonFactory.build()
    assert isinstance(person_instance.secret, CustomSecret)
    assert repr(person_instance.secret) == "*" * len("jeronimo")
    assert str(person_instance.secret) == "*" * len("jeronimo")
    assert person_instance.secret.value == "jeronimo"
