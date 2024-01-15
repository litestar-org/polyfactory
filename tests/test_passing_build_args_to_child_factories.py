from typing import List, Mapping, Optional

from pydantic import BaseModel

from polyfactory.factories.pydantic_factory import ModelFactory
from polyfactory.field_meta import FieldMeta


class Address(BaseModel):
    city: str
    country: str


class Material(BaseModel):
    name: str
    origin: str


class Toy(BaseModel):
    name: str
    weight: float
    materials: List[Material]


class Pet(BaseModel):
    name: str
    age: int
    toys: List[Toy]


class Person(BaseModel):
    name: str
    age: int
    pets: List[Pet]
    address: Address


class PersonFactory(ModelFactory):
    __model__ = Person


def test_factory_child_model_list() -> None:
    data = {
        "name": "Jean",
        "pets": [
            {
                "name": "dog",
                "toys": [
                    {
                        "name": "ball",
                        "materials": [{"name": "yarn"}, {"name": "plastic"}],
                    },
                    {
                        "name": "bone",
                    },
                ],
            },
            {
                "name": "cat",
            },
        ],
        "address": {
            "country": "France",
        },
    }

    person = PersonFactory.build(factory_use_construct=False, **data)

    assert person.name == "Jean"
    assert len(person.pets) == 2
    assert person.pets[0].name == "dog"
    dog = person.pets[0]
    assert len(dog.toys) == 2
    dog_toys = dog.toys
    assert dog_toys[0].name == "ball"
    assert len(dog.toys[0].materials) == 2
    assert dog.toys[0].materials[0].name == "yarn"
    assert dog.toys[0].materials[1].name == "plastic"
    assert len(dog.toys[1].materials) > 0
    assert dog.toys[1].name == "bone"
    assert person.pets[1].name == "cat"
    assert person.address.country == "France"


def test_factory_child_pydantic_model() -> None:
    """Given a Pydantic Factory, When I build a model using the factory passing a Pydantic model as attribute, Then the
    pydantic model is correctly built.
    """
    address = Address(city="Paris", country="France")
    person = PersonFactory.build(address=address)

    assert person.address.city == "Paris"
    assert person.address.country == "France"


def test_factory_child_none() -> None:
    """Given a Pydantic Factory, When I build a model using the factory passing None as attribute, Then the pydantic
    model is correctly built.
    """

    class PersonOptional(BaseModel):
        name: str
        address: Optional[Address]

    class PersonOptionalFactory(ModelFactory):
        __model__ = PersonOptional

    person = PersonOptionalFactory.build(address=None)
    assert person.address is None


def test_factory_with_partial_fields() -> None:
    """Given a Pydantic Model with nested Mapping field_meta, When I build the model using the factory passing only partial
    attributes, Then the model is correctly built.
    """

    class NestedSchema(BaseModel):
        v: str
        z: int

    class UpperSchema(BaseModel):
        a: int
        b: Mapping[str, str]
        nested: Mapping[str, NestedSchema]

    class UpperSchemaFactory(ModelFactory):
        __model__ = UpperSchema

    nested = NestedSchema(v="hello", z=0)
    some_dict = {"test": "fine"}
    upper = UpperSchemaFactory.build(b=some_dict, nested={"nested_key": nested})

    assert upper.b["test"] == "fine"
    assert "nested_key" in upper.nested
    assert upper.nested["nested_key"].v == nested.v
    assert upper.nested["nested_key"].z == nested.z


def test_factory_with_nested_dict() -> None:
    """Given a Pydantic Model with nested Dict field_meta, When I build the model using the factory passing only partial
    attributes, Then the model is correctly built.
    """

    class NestedSchema(BaseModel):
        z: int

    class UpperSchema(BaseModel):
        nested: Mapping[str, NestedSchema]

    class UpperSchemaFactory(ModelFactory):
        __model__ = UpperSchema

    nested = NestedSchema(z=0)
    upper = UpperSchemaFactory.build(nested={"nested_dict": nested})

    assert "nested_dict" in upper.nested
    assert upper.nested["nested_dict"].z == nested.z


def test_factory_with_partial_kwargs_deep_in_tree() -> None:
    class A(BaseModel):
        name: str
        age: int

    class B(BaseModel):
        a: A

    class C(BaseModel):
        b: B

    class D(BaseModel):
        c: C

    class DFactory(ModelFactory):
        __model__ = D

    build_result = DFactory.build(factory_use_construct=False, **{"c": {"b": {"a": {"name": "test"}}}})
    assert build_result
    assert build_result.c.b.a.name == "test"


def test_factory_with_nested_optional_field_overrides_in_dict() -> None:
    class MyChildModel(BaseModel):
        name: str

    class MyParentModel(BaseModel):
        child: Optional[MyChildModel]

    class MyParentModelFactory(ModelFactory):
        __model__ = MyParentModel

        @classmethod
        def should_set_none_value(cls, field_meta: FieldMeta) -> bool:
            return True

    result = MyParentModelFactory.build(child={"name": "test"})
    assert result.child is not None
    assert result.child.name == "test"
