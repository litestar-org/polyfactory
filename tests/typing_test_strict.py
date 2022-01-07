"""Module exists only to test generic boundaries.

Filename should not start with "test_".
"""
import dataclasses

import pydantic.dataclasses
from pydantic import BaseModel

from pydantic_factories import ModelFactory


class PydanticClass(BaseModel):
    field: str


class PydanticClassFactory(ModelFactory[PydanticClass]):
    __model__ = PydanticClass


@pydantic.dataclasses.dataclass
class PydanticDataClass:
    field: str


class PydanticDataClassFactory(ModelFactory[PydanticDataClass]):
    __model__ = PydanticDataClass


@dataclasses.dataclass()
class PythonDataClass:
    field: str


class PythonDataClassFactory(ModelFactory[PythonDataClass]):
    __model__ = PythonDataClass
