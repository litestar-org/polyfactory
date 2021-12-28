from dataclasses import dataclass as vanilla_dataclass
from uuid import uuid4

import pytest
from pydantic import ValidationError

from pydantic_factories import ModelFactory
from pydantic_factories.exceptions import ConfigurationError
from tests.models import PersonFactoryWithDefaults, Pet, PetFactory


def test_merges_defaults_with_kwargs():
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
    kwarg_id_id = uuid4()
    kwarg_id_hobbies = ["dancing"]
    kwarg_id_age = 35
    kwarg_id_pets = [pet]
    second_obj = PersonFactoryWithDefaults.build(
        id=kwarg_id_id, hobbies=kwarg_id_hobbies, age=kwarg_id_age, pets=kwarg_id_pets
    )
    assert second_obj.id == kwarg_id_id
    assert second_obj.hobbies == kwarg_id_hobbies
    assert second_obj.age == kwarg_id_age
    assert second_obj.pets == [pet]
    assert second_obj.name == PersonFactoryWithDefaults.name
    assert second_obj.birthday == PersonFactoryWithDefaults.birthday


def test_respects_none_overrides():
    result = PersonFactoryWithDefaults.build(hobbies=None)
    assert result.hobbies is None


def test_uses_faker_to_set_values_when_none_available_on_class():
    result = PetFactory.build()
    assert isinstance(result.name, str)
    assert isinstance(result.species, str)
    assert isinstance(result.color, str)
    assert isinstance(result.sound, str)
    assert isinstance(result.age, float)


def test_builds_batch():
    results = PetFactory.batch(10)
    assert isinstance(results, list)
    assert len(results) == 10
    for result in results:
        assert isinstance(result.name, str)
        assert isinstance(result.species, str)
        assert isinstance(result.color, str)
        assert isinstance(result.sound, str)
        assert isinstance(result.age, float)


def test_factory_use_construct():
    invalid_age = "non_valid_age"
    non_validated_pet = PetFactory.build(factory_use_construct=True, age=invalid_age)
    assert non_validated_pet.age == invalid_age

    with pytest.raises(ValidationError):
        PetFactory.build(factory_use_construct=False, age=invalid_age)

    with pytest.raises(ValidationError):
        PetFactory.build(age=invalid_age)

    @vanilla_dataclass
    class VanillaDC:
        id: int

    class MyFactory(ModelFactory):
        __model__ = VanillaDC

    with pytest.raises(ConfigurationError):
        MyFactory.build(factory_use_construct=True)
