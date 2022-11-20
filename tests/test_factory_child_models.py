from typing import Any, List, Mapping, Optional

from pydantic import BaseModel

from pydantic_factories import ModelFactory


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

    person = PersonFactory.build(**data)  # type: ignore

    expected_dict = {
        "name": "Jean",
        "age": AssertDict.random_int,
        "pets": [
            {
                "name": "dog",
                "age": AssertDict.random_int,
                "toys": [
                    {
                        "name": "ball",
                        "weight": AssertDict.random_float,
                        "materials": [
                            {"name": "yarn", "origin": AssertDict.random_str},
                            {"name": "plastic", "origin": AssertDict.random_str},
                        ],
                    },
                    {
                        "name": "bone",
                        "weight": AssertDict.random_float,
                        "materials": [
                            {"name": AssertDict.random_str, "origin": AssertDict.random_str},
                        ],
                    },
                ],
            },
            {
                "name": "cat",
                "age": AssertDict.random_int,
                "toys": [
                    {
                        "name": AssertDict.random_str,
                        "weight": AssertDict.random_float,
                        "materials": [
                            {"name": AssertDict.random_str, "origin": AssertDict.random_str},
                        ],
                    }
                ],
            },
        ],
        "address": {"city": AssertDict.random_str, "country": "France"},
    }
    AssertDict.assert_dict_expected_shape(expected_dict, person.dict())


def test_factory_child_pydantic_model() -> None:
    """Given a Pydantic Factory, When I build a model using the factory passing
    a Pydantic model as attribute, Then the pydantic model is correctly
    built."""
    address = Address(city="Paris", country="France")
    person = PersonFactory.build(address=address)

    assert person.address.city == "Paris"
    assert person.address.country == "France"


def test_factory_child_none() -> None:
    """Given a Pydantic Factory, When I build a model using the factory passing
    None as attribute, Then the pydantic model is correctly built."""

    class PersonOptional(BaseModel):
        name: str
        address: Optional[Address]

    class PersonOptionalFactory(ModelFactory):
        __model__ = PersonOptional

    person = PersonOptionalFactory.build(address=None)
    assert person.address is None


class AssertDict:
    random_float = "random_float"
    random_int = "random_int"
    random_str = "random_str"

    @staticmethod
    def assert_dict_expected_shape(expected_json: Any, json: Any) -> None:
        if isinstance(expected_json, list):
            assert len(expected_json) == len(json)
            for expected, actual in zip(expected_json, json):
                AssertDict.assert_dict_expected_shape(expected, actual)
        elif isinstance(expected_json, dict):
            for key, value in expected_json.items():
                assert key in json
                AssertDict.assert_dict_expected_shape(value, json[key])
        elif expected_json == AssertDict.random_float:
            assert isinstance(json, float)
        elif expected_json == AssertDict.random_int:
            assert isinstance(json, int)
        elif expected_json == AssertDict.random_str:
            assert isinstance(json, str)
        else:
            assert expected_json == json


def test_factory_not_ok() -> None:
    """Given a Pydantic Model with nested Mapping field, When I build the model
    using the factory passing only partial attributes, Then the model is
    correctly built."""

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
    """Given a Pydantic Model with nested Dict field, When I build the model
    using the factory passing only partial attributes, Then the model is
    correctly built."""

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
    # the code below is a modified copy of the bug reproduction example in
    # https://github.com/starlite-api/pydantic-factories/issues/115
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
