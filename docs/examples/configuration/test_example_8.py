from dataclasses import dataclass
from uuid import UUID

from polyfactory import PostGenerated
from polyfactory.factories.dataclass_factory import DataclassFactory


@dataclass
class Person:
    id: UUID


class PersonFactory(DataclassFactory[Person]):
    __model__ = Person
    __check_model__ = True
    unknown_field = PostGenerated(lambda: "foo")


def test_optional_type_ignored() -> None:
    PersonFactory()
    """
    The above will raise:
    polyfactory.exceptions.ConfigurationException: unknown_field is declared on the factory PersonFactory but it is not part of the model Person
    """
