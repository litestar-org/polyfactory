from datetime import date, datetime
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
    hobbies: list[str] | None
    nicks: list[str]
    age: float | int
    pets: list[Pet]
    birthday: datetime | date


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
