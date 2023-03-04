from datetime import date, datetime
from typing import List, Optional, Union
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
    hobbies: Optional[List[str]]
    nicks: List[str]
    age: Union[float, int]
    pets: List[Pet]
    birthday: Union[datetime, date]


class PersonFactoryWithoutDefaults(ModelFactory):
    __model__ = Person


class PersonFactoryWithDefaults(PersonFactoryWithoutDefaults):
    id = uuid4()
    name = "moishe"
    hobbies = ["fishing"]
    nicks: List[str] = []
    age = 33
    pets: List[Pet] = []
    birthday = datetime(2021 - 33, 1, 1)


class PetFactory(ModelFactory):
    __model__ = Pet
