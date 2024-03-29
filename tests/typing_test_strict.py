"""Module exists only to test generic boundaries.

Filename should not start with "test_".
"""

import dataclasses
from typing import TypedDict

import pydantic.dataclasses
from pydantic import BaseModel

from polyfactory.factories import DataclassFactory, TypedDictFactory
from polyfactory.factories.pydantic_factory import ModelFactory


class PydanticClass(BaseModel):
    field: str


class PydanticClassFactory(ModelFactory[PydanticClass]):
    __model__ = PydanticClass


@pydantic.dataclasses.dataclass
class PydanticDataClass:
    field: str


class PydanticDataClassFactory(DataclassFactory[PydanticDataClass]):
    __model__ = PydanticDataClass


@dataclasses.dataclass()
class PythonDataClass:
    field: str


class PythonDataClassFactory(DataclassFactory[PythonDataClass]):
    __model__ = PythonDataClass


class TypedDictClass(TypedDict):
    field: str


class TypedDictClassFactory(TypedDictFactory[TypedDictClass]):
    __model__ = TypedDictClass
