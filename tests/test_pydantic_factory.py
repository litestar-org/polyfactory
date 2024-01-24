import sys
from typing import Dict, List, Optional, Set, Tuple

import pytest
from typing_extensions import Annotated

from pydantic import VERSION, BaseModel, Field, Json, ValidationError

from polyfactory.factories.pydantic_factory import ModelFactory
from tests.models import PetFactory


@pytest.mark.skipif(VERSION.startswith("2"), reason="pydantic v1 only functionality")
def test_const() -> None:
    class A(BaseModel):
        v: int = Field(1, const=True)  # type: ignore[call-arg]

    class AFactory(ModelFactory[A]):
        __model__ = A

    for _ in range(5):
        assert AFactory.build()


def test_optional_with_constraints() -> None:
    class A(BaseModel):
        a: Optional[float] = Field(None, ge=0, le=1)

    class AFactory(ModelFactory[A]):
        __model__ = A
        # Setting random seed so that we get a non-optional value
        random_seed = 1

        __random_seed__ = random_seed

    # verify no pydantic.ValidationError is thrown
    assert isinstance(AFactory.build().a, float)


@pytest.mark.skipif(sys.version_info < (3, 10), reason="requires python3.9 or higher")
def test_list_unions() -> None:
    # issue: https://github.com/litestar-org/polyfactory/issues/300, no error reproduced
    class A(BaseModel):
        a: str

    class B(BaseModel):
        b: str

    class C(BaseModel):
        c: list[A] | list[B]

    class CFactory(ModelFactory[C]):
        __forward_ref_resolution_type_mapping__ = {"A": A, "B": B, "C": C}
        __model__ = C

    assert isinstance(CFactory.build().c, list)
    assert len(CFactory.build().c) > 0
    assert isinstance(CFactory.build().c[0], (A, B))


@pytest.mark.skipif(VERSION.startswith("1"), reason="only for Pydantic v2")
def test_json_type() -> None:
    class A(BaseModel):
        a: Json[int]

    class AFactory(ModelFactory[A]):
        __model__ = A

    assert isinstance(AFactory.build(), A)


@pytest.mark.skipif(VERSION.startswith("1"), reason="only for Pydantic v2")
def test_nested_json_type() -> None:
    class A(BaseModel):
        a: int

    class B(BaseModel):
        b: Json[A]

    class BFactory(ModelFactory[B]):
        __model__ = B

    assert isinstance(BFactory.build(), B)


def test_sequence_with_annotated_item_types() -> None:
    ConstrainedInt = Annotated[int, Field(ge=100, le=200)]

    class Foo(BaseModel):
        list_field: List[ConstrainedInt]
        tuple_field: Tuple[ConstrainedInt]
        variable_tuple_field: Tuple[ConstrainedInt, ...]
        set_field: Set[ConstrainedInt]

    class FooFactory(ModelFactory[Foo]):
        __model__ = Foo

    assert FooFactory.build()


def test_mapping_with_annotated_item_types() -> None:
    ConstrainedInt = Annotated[int, Field(ge=100, le=200)]
    ConstrainedStr = Annotated[str, Field(min_length=1, max_length=3)]

    class Foo(BaseModel):
        dict_field: Dict[ConstrainedStr, ConstrainedInt]

    class FooFactory(ModelFactory[Foo]):
        __model__ = Foo

    assert FooFactory.build()


def test_use_default_with_callable_default() -> None:
    class Foo(BaseModel):
        default_field: int = Field(default_factory=lambda: 10)

    class FooFactory(ModelFactory[Foo]):
        __model__ = Foo
        __use_defaults__ = True

    foo = FooFactory.build()

    assert foo.default_field == 10


def test_use_default_with_non_callable_default() -> None:
    class Foo(BaseModel):
        default_field: int = Field(default=10)

    class FooFactory(ModelFactory[Foo]):
        __model__ = Foo
        __use_defaults__ = True

    foo = FooFactory.build()

    assert foo.default_field == 10


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
