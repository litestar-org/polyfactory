from pydantic import BaseModel

from polyfactory.factories.pydantic_factory import ModelFactory


class Person(BaseModel):
    name: str
    age: float
    height: float
    weight: float


class PersonFactory(ModelFactory[Person]): ...


def test_is_person() -> None:
    person_instance = PersonFactory.build()
    assert isinstance(person_instance, Person)
    assert isinstance(person_instance.name, str)
    assert isinstance(person_instance.age, float)
    assert isinstance(person_instance.height, float)
    assert isinstance(person_instance.weight, float)
