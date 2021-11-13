from datetime import date, datetime
from typing import Optional, Union
from uuid import UUID, uuid4

from pydantic import BaseModel

from pydantic_factories.factory import ModelFactory


class Pet(BaseModel):
    name: str
    species: str
    color: str
    sound: str
    age: float


class Person(BaseModel):
    id: UUID
    name: str
    hobbies: Optional[list[str]] = None
    age: float
    pets: list[Pet]
    birthday: Union[datetime, date]


def test_merges_defaults_with_kwargs():
    factory = ModelFactory(
        id=uuid4(),
        model=Person,
        name="moishe",
        hobbies=["fishing"],
        age=33,
        pets=[],
        birthday=datetime(2021 - 33, 1, 1),
    )
    first_obj = factory.build()
    assert first_obj.name == "moishe"
    assert first_obj.hobbies == ["fishing"]
    assert first_obj.age == 33.0
    assert first_obj.pets == []
    pet = Pet(
        name="bluey the blowfish",
        species="blowfish",
        color="bluish-green",
        sound="",
        age=1,
    )
    second_obj = factory.build(id=uuid4(), hobbies=["dancing"], age=35, pets=[pet], birthday=datetime(2021 - 35, 1, 1))
    assert first_obj.name == "moishe"
    assert second_obj.hobbies == ["dancing"]
    assert second_obj.age == 35.0
    assert second_obj.pets == [pet]
