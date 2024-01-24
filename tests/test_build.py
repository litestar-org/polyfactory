from uuid import uuid4

from pydantic import BaseModel

from polyfactory.factories.pydantic_factory import ModelFactory
from tests.models import PersonFactoryWithDefaults, Pet, PetFactory


def test_merges_defaults_with_kwargs() -> None:
    first_obj = PersonFactoryWithDefaults.build()
    assert first_obj.id == PersonFactoryWithDefaults.id
    assert first_obj.name == PersonFactoryWithDefaults.name
    assert first_obj.hobbies == PersonFactoryWithDefaults.hobbies
    assert first_obj.age == PersonFactoryWithDefaults.age
    assert first_obj.pets == PersonFactoryWithDefaults.pets
    assert first_obj.birthday == PersonFactoryWithDefaults.birthday
    pet = Pet(
        name="bluey the blowfish",
        species="blowfish",
        color="bluish-green",
        sound="",
        age=1,
    )
    id_ = uuid4()
    hobbies = ["dancing"]
    age = 35
    pets = [pet]
    second_obj = PersonFactoryWithDefaults.build(id=id_, hobbies=hobbies, age=age, pets=pets)
    assert second_obj.id == id_
    assert second_obj.hobbies == hobbies
    assert second_obj.age == age
    assert second_obj.pets == [pet]
    assert second_obj.name == PersonFactoryWithDefaults.name
    assert second_obj.birthday == PersonFactoryWithDefaults.birthday


def test_respects_none_overrides() -> None:
    result = PersonFactoryWithDefaults.build(hobbies=None)
    assert result.hobbies is None


def test_uses_faker_to_set_values_when_none_available_on_class() -> None:
    result = PetFactory.build()
    assert isinstance(result.name, str)
    assert isinstance(result.species, str)
    assert isinstance(result.color, str)
    assert isinstance(result.sound, str)
    assert isinstance(result.age, float)


def test_builds_batch() -> None:
    results = PetFactory.batch(10)
    assert isinstance(results, list)
    assert len(results) == 10
    for result in results:
        assert isinstance(result.name, str)
        assert isinstance(result.species, str)
        assert isinstance(result.color, str)
        assert isinstance(result.sound, str)
        assert isinstance(result.age, float)


def test_build_model_with_fields_named_like_factory_fields() -> None:
    class C(BaseModel):
        batch: int

    class CFactory(ModelFactory):
        __model__ = C

    assert CFactory.build()
