from __future__ import annotations

from dataclasses import dataclass
from typing import Union

from polyfactory.factories import DataclassFactory

# Define a recursive type using forward reference
RecursiveType = Union[list["RecursiveType"], int]


@dataclass
class RecursiveTypeModel:
    recursive_value: RecursiveType


class RecursiveTypeModelFactory(DataclassFactory[RecursiveTypeModel]):
    __forward_references__ = {"RecursiveType": int}


def test_forward_references() -> None:
    factory = RecursiveTypeModelFactory()
    result = factory.build().recursive_value
    assert isinstance(result, int) or (isinstance(result, list) and all(isinstance(value, int) for value in result))
