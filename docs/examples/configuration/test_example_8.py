from dataclasses import dataclass
from uuid import UUID

import pytest

from polyfactory import ConfigurationException, PostGenerated
from polyfactory.factories.dataclass_factory import DataclassFactory


@dataclass
class Person:
    id: UUID


def test_check_factory_fields() -> None:
    with pytest.raises(
        ConfigurationException,
        match="unknown_field is declared on the factory PersonFactory but it is not part of the model Person",
    ):

        class PersonFactory(DataclassFactory[Person]):
            __check_model__ = True
            unknown_field = PostGenerated(lambda: "foo")
