from datetime import date, datetime
from typing import Optional, Union
from uuid import uuid4

from pydantic import UUID4, BaseModel

from polyfactory.factories.pydantic_factory import ModelFactory


class Pet(BaseModel):
    name: str
    species: str
    color: str
    sound: str
    age: float


class Person(BaseModel):
    id: UUID4
    name: str
    hobbies: Optional[list[str]]
    nicks: list[str]
    age: Union[float, int]
    pets: list[Pet]
    birthday: Union[datetime, date]


class PersonFactoryWithoutDefaults(ModelFactory[Person]):
    __model__ = Person


class PersonFactoryWithDefaults(PersonFactoryWithoutDefaults):
    id = uuid4()
    name = "moishe"
    hobbies = ["fishing"]
    nicks: list[str] = []
    age = 33
    pets: list[Pet] = []
    birthday = datetime(2021 - 33, 1, 1)


class PetFactory(ModelFactory[Pet]):
    __model__ = Pet
