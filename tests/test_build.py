from uuid import uuid4

import pytest
from pydantic import VERSION, BaseModel, Field, ValidationError

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


def test_factory_use_construct() -> None:
    # factory should pass values without validation
    invalid_age = "non_valid_age"
    non_validated_pet = PetFactory.build(factory_use_construct=True, age=invalid_age)
    assert non_validated_pet.age == invalid_age

    with pytest.raises(ValidationError):
        PetFactory.build(age=invalid_age)

    with pytest.raises(ValidationError):
        PetFactory.build(age=invalid_age)


@pytest.mark.skipif(VERSION.startswith("2"), reason="pydantic 1 only test")
def test_build_instance_by_field_alias_with_allow_population_by_field_name_flag_pydantic_v1() -> None:
    class MyModel(BaseModel):
        aliased_field: str = Field(..., alias="special_field")

        class Config:
            allow_population_by_field_name = True

    class MyFactory(ModelFactory):
        __model__ = MyModel

    instance = MyFactory.build(aliased_field="some")
    assert instance.aliased_field == "some"


@pytest.mark.skipif(VERSION.startswith("1"), reason="pydantic 2 only test")
def test_build_instance_by_field_alias_with_populate_by_name_flag_pydantic_v2() -> None:
    class MyModel(BaseModel):
        model_config = {"populate_by_name": True}
        aliased_field: str = Field(..., alias="special_field")

    class MyFactory(ModelFactory):
        __model__ = MyModel

    instance = MyFactory.build(aliased_field="some")
    assert instance.aliased_field == "some"


def test_build_instance_by_field_name_with_allow_population_by_field_name_flag() -> None:
    class MyModel(BaseModel):
        aliased_field: str = Field(..., alias="special_field")

        class Config:
            allow_population_by_field_name = True

    class MyFactory(ModelFactory):
        __model__ = MyModel

    instance = MyFactory.build(special_field="some")
    assert instance.aliased_field == "some"


def test_build_model_with_fields_named_like_factory_fields() -> None:
    class C(BaseModel):
        batch: int

    class CFactory(ModelFactory):
        __model__ = C

    assert CFactory.build()
