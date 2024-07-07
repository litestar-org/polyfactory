import re
import sys
from collections import Counter, deque
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from decimal import Decimal
from ipaddress import (
    IPv4Address,
    IPv4Interface,
    IPv4Network,
    IPv6Address,
    IPv6Interface,
    IPv6Network,
)
from pathlib import Path
from typing import Callable, Dict, FrozenSet, List, Literal, Optional, Sequence, Set, Tuple, Type, Union
from uuid import UUID

import pytest
from annotated_types import Ge, Gt, Le, LowerCase, MinLen, UpperCase
from typing_extensions import Annotated, TypeAlias

import pydantic
from pydantic import (
    UUID1,
    UUID3,
    UUID4,
    UUID5,
    AmqpDsn,
    AnyHttpUrl,
    AnyUrl,
    BaseModel,
    ByteSize,
    DirectoryPath,
    EmailStr,
    Field,
    FilePath,
    FutureDate,
    HttpUrl,
    IPvAnyAddress,
    IPvAnyInterface,
    IPvAnyNetwork,
    Json,
    KafkaDsn,
    NameEmail,
    NegativeFloat,
    NegativeInt,
    NonNegativeInt,
    NonPositiveFloat,
    PastDate,
    PositiveFloat,
    PositiveInt,
    PostgresDsn,
    RedisDsn,
    SecretBytes,
    SecretStr,
    StrictBool,
    StrictBytes,
    StrictFloat,
    StrictInt,
    StrictStr,
    ValidationError,
    conbytes,
    condecimal,
    confloat,
    confrozenset,
    conint,
    conlist,
    conset,
    constr,
    validator,
)

from polyfactory.factories import DataclassFactory
from polyfactory.factories.pydantic_factory import _IS_PYDANTIC_V1, ModelFactory
from tests.models import Person, PetFactory

IS_PYDANTIC_V1 = _IS_PYDANTIC_V1
IS_PYDANTIC_V2 = not _IS_PYDANTIC_V1
REGEX_PATTERN = r"(a|b|c)zz"


@pytest.mark.skipif(IS_PYDANTIC_V2, reason="pydantic v1 only functionality")
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


@pytest.mark.skipif(IS_PYDANTIC_V1, reason="only for Pydantic v2")
def test_json_type() -> None:
    class A(BaseModel):
        a: Json[int]

    class AFactory(ModelFactory[A]):
        __model__ = A

    assert isinstance(AFactory.build(), A)


@pytest.mark.skipif(IS_PYDANTIC_V1, reason="only for Pydantic v2")
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


def test_factory_use_construct_coverage() -> None:
    class Foo(BaseModel):
        invalid: int

        @validator("invalid")
        @classmethod
        def always_invalid(cls, v: int) -> None:
            raise ValueError("invalid by validator")

    class FooFactory(ModelFactory[Foo]):
        __model__ = Foo

    non_validated = list(FooFactory.coverage(factory_use_construct=True))
    assert len(non_validated) == 1

    with pytest.raises(ValidationError):
        FooFactory.build()


def test_factory_use_construct_nested() -> None:
    class Child(BaseModel):
        a: int = Field(ge=0)

    class Parent(BaseModel):
        child: Child

    class ParentFactory(ModelFactory[Parent]):
        __model__ = Parent

    non_validated_parent = ParentFactory.build(factory_use_construct=True, child={"a": -1})
    assert non_validated_parent.child.a == -1

    with pytest.raises(ValidationError):
        ParentFactory.build(child={"a": -1})


def test_factory_use_construct_validator() -> None:
    class Foo(BaseModel):
        invalid: int

        @validator("invalid")
        @classmethod
        def always_invalid(cls, v: int) -> None:
            raise ValueError("invalid by validator")

    class FooFactory(ModelFactory[Foo]):
        __model__ = Foo

    non_validated = FooFactory.build(factory_use_construct=True)
    assert isinstance(non_validated.invalid, int)

    with pytest.raises(ValidationError):
        FooFactory.build()


@pytest.mark.parametrize("sequence_type", (Tuple, List))
def test_factory_use_construct_nested_sequence(sequence_type: Type[Sequence]) -> None:
    class Child(BaseModel):
        a: int = Field(ge=0)

    class Parent(BaseModel):
        child: sequence_type[Child]  # type: ignore[valid-type]

    class ParentFactory(ModelFactory[Parent]):
        __model__ = Parent

    non_validated_parent = ParentFactory.build(factory_use_construct=True, child=[{"a": -1}])
    assert len(non_validated_parent.child) == 1

    with pytest.raises(ValidationError):
        ParentFactory.build(child=[{"a": -1}])


@pytest.mark.parametrize("set_type", (FrozenSet, Set))
def test_factory_use_construct_nested_set(set_type: Union[Type[FrozenSet], Type[Set]]) -> None:
    class Child(BaseModel):
        invalid: int = Field()

        @validator("invalid", allow_reuse=True)
        @classmethod
        def always_invalid(cls, v: int) -> None:
            raise ValueError("invalid by validator")

        def __hash__(self) -> int:
            return hash(self.invalid)

    class Parent(BaseModel):
        child: set_type[Child]  # type: ignore[valid-type]

    class ParentFactory(ModelFactory[Parent]):
        __model__ = Parent

    non_validated_parent = ParentFactory.build(factory_use_construct=True)
    assert len(non_validated_parent.child) == 1
    assert isinstance(non_validated_parent.child, set_type)

    with pytest.raises(ValidationError):
        ParentFactory.build()


def test_mapping_with_annotated_nested_model() -> None:
    class ChildValue(BaseModel):
        a: int = Field(ge=0)

    class Parent(BaseModel):
        dict_field: Dict[str, ChildValue]

    class ParentFactory(ModelFactory[Parent]):
        __model__ = Parent

    non_validated_parent = ParentFactory.build(factory_use_construct=True, dict_field={"arb": {"a": -1}})

    assert set(non_validated_parent.dict_field) == {"arb"}
    # not converted
    assert non_validated_parent.dict_field["arb"] == {"a": -1}  # type: ignore[comparison-overlap]

    with pytest.raises(ValidationError):
        assert ParentFactory.build(dict_field={"arb": {"a": -1}})


@pytest.mark.skipif(
    True,
    reason=(
        "pydantic 1 only test, "
        "get_args function not returning the origin type as expected for pydantic v1 constrained values, "
        "ex. ConstrainedListValue. "
    ),
)
def test_factory_use_construct_nested_constraint_list_v1() -> None:
    class Child(BaseModel):
        a: int = Field(ge=0)

    class Parent(BaseModel):
        child: conlist(Child, min_items=1, max_items=4)  # type: ignore[valid-type]
        child_annotated: Annotated[List[Child], Field(min_items=1, max_items=4)]

    class ParentFactory(ModelFactory[Parent]):
        __model__ = Parent

    non_validated_parent = ParentFactory.build(
        factory_use_construct=True, child=[{"a": -1}], child_annotated=[{"a": -2}]
    )
    assert non_validated_parent.child[0].a == -1
    assert non_validated_parent.child_annotated[0].a == -2

    with pytest.raises(ValidationError):
        ParentFactory.build(child=[{"a": -1}])

    with pytest.raises(ValidationError):
        ParentFactory.build(child_annotated=[{"a": -1}])


@pytest.mark.skipif(IS_PYDANTIC_V1, reason="pydantic 2 only test")
def test_factory_use_construct_nested_constraint_list_v2() -> None:
    class Child(BaseModel):
        a: int = Field(ge=0)

    class Parent(BaseModel):
        child: conlist(Child, min_length=1, max_length=4)  # type: ignore[valid-type]
        child_annotated: Annotated[List[Child], Field(min_length=1, max_length=4)]

    class ParentFactory(ModelFactory[Parent]):
        __model__ = Parent

    non_validated_parent = ParentFactory.build(
        factory_use_construct=True, child=[{"a": -1}], child_annotated=[{"a": -2}]
    )
    assert non_validated_parent.child[0].a == -1
    assert non_validated_parent.child_annotated[0].a == -2

    with pytest.raises(ValidationError):
        ParentFactory.build(child=[{"a": -1}])

    with pytest.raises(ValidationError):
        ParentFactory.build(child_annotated=[{"a": -1}])


@pytest.mark.skipif(IS_PYDANTIC_V2, reason="pydantic 1 only test")
def test_build_instance_by_field_alias_with_allow_population_by_field_name_flag_pydantic_v1() -> None:
    class MyModel(BaseModel):
        aliased_field: str = Field(..., alias="special_field")

        class Config:
            allow_population_by_field_name = True

    class MyFactory(ModelFactory):
        __model__ = MyModel

    instance = MyFactory.build(aliased_field="some")
    assert instance.aliased_field == "some"


@pytest.mark.skipif(IS_PYDANTIC_V1, reason="pydantic 2 only test")
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


def test_alias_parsing() -> None:
    class MyModel(BaseModel):
        aliased_field: str = Field(alias="special_field")

    class MyFactory(ModelFactory):
        __model__ = MyModel

    assert isinstance(MyFactory.build().aliased_field, str)


def test_type_property_parsing() -> None:
    class Base(BaseModel):
        if IS_PYDANTIC_V2:
            MongoDsn_pydantic_type: pydantic.networks.MongoDsn
            MariaDBDsn_pydantic_type: pydantic.networks.MariaDBDsn
            CockroachDsn_pydantic_type: pydantic.networks.CockroachDsn
            MySQLDsn_pydantic_type: pydantic.networks.MySQLDsn
            PastDatetime_pydantic_type: pydantic.PastDatetime
            FutureDatetime_pydantic_type: pydantic.FutureDatetime
            AwareDatetime_pydantic_type: pydantic.AwareDatetime
            NaiveDatetime_pydantic_type: pydantic.NaiveDatetime

        else:
            PyObject_pydantic_type: pydantic.types.PyObject
            Color_pydantic_type: pydantic.color.Color

    class MyModel(Base):
        object_field: object
        float_field: float
        int_field: int
        bool_field: bool
        str_field: str
        bytes_field: bytes
        # built-in objects
        dict_field: dict
        tuple_field: tuple
        list_field: list
        set_field: set
        frozenset_field: frozenset
        deque_field: deque
        # standard library objects
        Path_field: Path
        Decimal_field: Decimal
        UUID_field: UUID
        # datetime
        datetime_field: datetime
        date_field: date
        time_field: time
        timedelta_field: timedelta
        # ip addresses
        IPv4Address_field: IPv4Address
        IPv4Interface_field: IPv4Interface
        IPv4Network_field: IPv4Network
        IPv6Address_field: IPv6Address
        IPv6Interface_field: IPv6Interface
        IPv6Network_field: IPv6Network
        # types
        Callable_field: Callable
        # pydantic specific
        ByteSize_pydantic_type: ByteSize
        PositiveInt_pydantic_type: PositiveInt
        FilePath_pydantic_type: FilePath
        NegativeFloat_pydantic_type: NegativeFloat
        NegativeInt_pydantic_type: NegativeInt
        PositiveFloat_pydantic_type: PositiveFloat
        NonPositiveFloat_pydantic_type: NonPositiveFloat
        NonNegativeInt_pydantic_type: NonNegativeInt
        StrictInt_pydantic_type: StrictInt
        StrictBool_pydantic_type: StrictBool
        StrictBytes_pydantic_type: StrictBytes
        StrictFloat_pydantic_type: StrictFloat
        StrictStr_pydantic_type: StrictStr
        DirectoryPath_pydantic_type: DirectoryPath
        EmailStr_pydantic_type: EmailStr
        NameEmail_pydantic_type: NameEmail
        Json_pydantic_type: Json
        AnyUrl_pydantic_type: AnyUrl
        AnyHttpUrl_pydantic_type: AnyHttpUrl
        HttpUrl_pydantic_type: HttpUrl
        PostgresDsn_pydantic_type: PostgresDsn
        RedisDsn_pydantic_type: RedisDsn
        UUID1_pydantic_type: UUID1
        UUID3_pydantic_type: UUID3
        UUID4_pydantic_type: UUID4
        UUID5_pydantic_type: UUID5
        SecretBytes_pydantic_type: SecretBytes
        SecretStr_pydantic_type: SecretStr
        IPvAnyAddress_pydantic_type: IPvAnyAddress
        IPvAnyInterface_pydantic_type: IPvAnyInterface
        IPvAnyNetwork_pydantic_type: IPvAnyNetwork
        AmqpDsn_pydantic_type: AmqpDsn
        KafkaDsn_pydantic_type: KafkaDsn
        PastDate_pydantic_type: PastDate
        FutureDate_pydantic_type: FutureDate
        Counter_pydantic_type: Counter

    class MyFactory(ModelFactory):
        __model__ = MyModel

    result = MyFactory.build()

    for key in MyFactory.get_provider_map():
        key_name = key.__name__ if hasattr(key, "__name__") else key._name
        if hasattr(result, f"{key_name}_field"):
            assert isinstance(getattr(result, f"{key_name}_field"), key)
        elif hasattr(result, f"{key_name}_pydantic_type"):
            assert getattr(result, f"{key_name}_pydantic_type") is not None


@pytest.mark.parametrize(
    "type_",
    [AnyUrl, HttpUrl, KafkaDsn, PostgresDsn, RedisDsn, AmqpDsn, AnyHttpUrl],
)
def test_optional_url_field_parsed_correctly(type_: TypeAlias) -> None:
    class MyModel(BaseModel):
        url: Optional[type_]

    class MyFactory(ModelFactory[MyModel]):
        __model__ = MyModel

    while not (url := MyFactory.build().url):
        assert not url

    assert MyModel(url=url)  # no validation error raised


@pytest.mark.skipif(IS_PYDANTIC_V2, reason="pydantic 1 only test")
def test_handles_complex_typing_with_custom_root_type() -> None:
    class MyModel(BaseModel):
        __root__: List[int]

    class MyFactory(ModelFactory[MyModel]):
        __model__ = MyModel

    result = MyFactory.build()

    assert result.__root__
    assert isinstance(result.__root__, list)


def test_union_types() -> None:
    class A(BaseModel):
        a: Union[List[str], List[int]]
        b: Union[str, List[int]]
        c: List[Union[Tuple[int, int], Tuple[str, int]]]

    AFactory = ModelFactory.create_factory(A)

    assert AFactory.build()


def test_collection_unions_with_models() -> None:
    class A(BaseModel):
        a: int

    class B(BaseModel):
        a: str

    class C(BaseModel):
        a: Union[List[A], List[B]]
        b: List[Union[A, B]]

    CFactory = ModelFactory.create_factory(C)

    assert CFactory.build()


def test_constrained_union_types() -> None:
    class A(BaseModel):
        a: Union[Annotated[List[str], MinLen(100)], Annotated[int, Ge(1000)]]
        b: Union[List[Annotated[str, MinLen(100)]], int]
        c: Union[Annotated[List[int], MinLen(100)], None]
        d: Union[Annotated[List[int], MinLen(100)], Annotated[List[str], MinLen(100)]]
        e: Optional[Union[Annotated[List[int], MinLen(10)], Annotated[List[str], MinLen(10)]]]
        f: Optional[Union[Annotated[List[int], MinLen(10)], List[str]]]

    AFactory = ModelFactory.create_factory(A, __allow_none_optionals__=False)

    assert AFactory.build()


@pytest.mark.parametrize("allow_none", (True, False))
def test_optional_type(allow_none: bool) -> None:
    class A(BaseModel):
        a: Union[str, None]
        b: Optional[str]
        c: Optional[Union[str, int, List[int]]]

    class AFactory(ModelFactory[A]):
        __model__ = A

        __allow_none_optionals__ = allow_none

    assert AFactory.build()


def test_discriminated_unions() -> None:
    class BasePet(BaseModel):
        name: str

    class BlackCat(BasePet):
        pet_type: Literal["cat"]
        color: Literal["black"]

    class WhiteCat(BasePet):
        pet_type: Literal["cat"]
        color: Literal["white"]

    class Dog(BasePet):
        pet_type: Literal["dog"]

    class Owner(BaseModel):
        pet: Annotated[
            Union[Annotated[Union[BlackCat, WhiteCat], Field(discriminator="color")], Dog],
            Field(discriminator="pet_type"),
        ]
        name: str

    class OwnerFactory(ModelFactory):
        __model__ = Owner

    assert OwnerFactory.build()


def test_predicated_fields() -> None:
    @dataclass
    class PredicatedMusician:
        name: Annotated[str, UpperCase]
        band: Annotated[str, LowerCase]

    class PredicatedMusicianFactory(DataclassFactory):
        __model__ = PredicatedMusician

    assert PredicatedMusicianFactory.build()


def test_tuple_with_annotated_constraints() -> None:
    class Location(BaseModel):
        long_lat: Tuple[Annotated[float, Ge(-180), Le(180)], Annotated[float, Ge(-90), Le(90)]]

    class LocationFactory(ModelFactory[Location]):
        __model__ = Location

    assert LocationFactory.build()


def test_optional_tuple_with_annotated_constraints() -> None:
    class Location(BaseModel):
        long_lat: Union[Tuple[Annotated[float, Ge(-180), Le(180)], Annotated[float, Ge(-90), Le(90)]], None]

    class LocationFactory(ModelFactory[Location]):
        __model__ = Location

    assert LocationFactory.build()


def test_legacy_tuple_with_annotated_constraints() -> None:
    class Location(BaseModel):
        long_lat: Tuple[Annotated[float, Ge(-180), Le(180)], Annotated[float, Ge(-90), Le(90)]]

    class LocationFactory(ModelFactory[Location]):
        __model__ = Location

    assert LocationFactory.build()


def test_legacy_optional_tuple_with_annotated_constraints() -> None:
    class Location(BaseModel):
        long_lat: Union[Tuple[Annotated[float, Ge(-180), Le(180)], Annotated[float, Ge(-90), Le(90)]], None]

    class LocationFactory(ModelFactory[Location]):
        __model__ = Location

    assert LocationFactory.build()


@pytest.mark.skipif(IS_PYDANTIC_V2, reason="pydantic 1 only test")
def test_constrained_attribute_parsing_pydantic_v1() -> None:
    class ConstrainedModel(BaseModel):
        conbytes_field: conbytes()  # type: ignore[valid-type]
        condecimal_field: condecimal()  # type: ignore[valid-type]
        confloat_field: confloat()  # type: ignore[valid-type]
        conint_field: conint()  # type: ignore[valid-type]
        conlist_field: conlist(str, min_items=5, max_items=10)  # type: ignore[valid-type]
        conset_field: conset(str, min_items=5, max_items=10)  # type: ignore[valid-type]
        confrozenset_field: confrozenset(str, min_items=5, max_items=10)  # type: ignore[valid-type]
        constr_field: constr(to_lower=True)  # type: ignore[valid-type]
        str_field1: str = Field(min_length=11)
        str_field2: str = Field(max_length=11)
        str_field3: str = Field(min_length=8, max_length=11, regex=REGEX_PATTERN)  # type: ignore[call-arg]
        int_field: int = Field(gt=1, multiple_of=5)
        float_field: float = Field(gt=100, lt=1000)
        decimal_field: Decimal = Field(ge=100, le=1000)
        list_field: List[str] = Field(min_items=1, max_items=10)  # type: ignore[call-arg]
        constant_field: int = Field(const=True, default=100)  # type: ignore[call-arg]
        optional_field: Optional[constr(min_length=1)]  # type: ignore[valid-type]

    class MyFactory(ModelFactory):
        __model__ = ConstrainedModel

    result = MyFactory.build()

    assert isinstance(result.conbytes_field, bytes)
    assert isinstance(result.conint_field, int)
    assert isinstance(result.confloat_field, float)
    assert isinstance(result.condecimal_field, Decimal)
    assert isinstance(result.conlist_field, list)
    assert isinstance(result.conset_field, set)
    assert isinstance(result.confrozenset_field, frozenset)
    assert isinstance(result.str_field1, str)
    assert isinstance(result.constr_field, str)
    assert len(result.conlist_field) >= 5
    assert len(result.conlist_field) <= 10
    assert len(result.conset_field) >= 5
    assert len(result.conset_field) <= 10
    assert len(result.confrozenset_field) >= 5
    assert len(result.confrozenset_field) <= 10
    assert result.constr_field.lower() == result.constr_field
    assert len(result.str_field1) >= 11
    assert len(result.str_field2) <= 11
    assert len(result.str_field3) >= 8
    assert len(result.str_field3) <= 11
    match = re.search(REGEX_PATTERN, result.str_field3)
    assert match
    assert match[0]
    assert result.int_field >= 1
    assert result.int_field % 5 == 0
    assert result.float_field > 100
    assert result.float_field < 1000
    assert result.decimal_field > 100
    assert result.decimal_field < 1000
    assert len(result.list_field) >= 1
    assert len(result.list_field) <= 10
    assert all(isinstance(r, str) for r in result.list_field)
    assert result.constant_field == 100
    assert result.optional_field is None or len(result.optional_field) >= 1


@pytest.mark.skipif(IS_PYDANTIC_V2, reason="pydantic 1 only test")
def test_complex_constrained_attribute_parsing_pydantic_v1() -> None:
    class MyModel(BaseModel):
        conlist_with_model_field: conlist(Person, min_items=3)  # type: ignore[valid-type]
        conlist_with_complex_type: conlist(  # type: ignore[valid-type]
            Dict[str, Tuple[Person, Person, Person]],
            min_items=1,
        )

    class MyFactory(ModelFactory):
        __model__ = MyModel

    result = MyFactory.build()

    assert len(result.conlist_with_model_field) >= 3
    assert all(isinstance(v, Person) for v in result.conlist_with_model_field)
    assert result.conlist_with_complex_type
    assert isinstance(result.conlist_with_complex_type[0], dict)
    assert isinstance(next(iter(result.conlist_with_complex_type[0].values())), tuple)
    assert len(next(iter(result.conlist_with_complex_type[0].values()))) == 3
    assert all(isinstance(v, Person) for v in next(iter(result.conlist_with_complex_type[0].values())))


@pytest.mark.skipif(IS_PYDANTIC_V2, reason="pydantic 1 only test")
def test_nested_constrained_attribute_handling_pydantic_1() -> None:
    # subclassing the constrained fields is not documented by pydantic,
    # but is supported apparently

    from pydantic import (
        ConstrainedBytes,
        ConstrainedDecimal,
        ConstrainedFloat,
        ConstrainedInt,
        ConstrainedStr,
    )

    class MyConstrainedString(ConstrainedStr):  # type: ignore[misc,valid-type]
        regex = re.compile("^vpc-.*$")

    class MyConstrainedBytes(ConstrainedBytes):  # type: ignore[misc,valid-type]
        min_length = 11

    class MyConstrainedInt(ConstrainedInt):  # type: ignore[misc,valid-type]
        ge = 11

    class MyConstrainedFloat(ConstrainedFloat):  # type: ignore[misc,valid-type]
        ge = 11.0

    class MyConstrainedDecimal(ConstrainedDecimal):  # type: ignore[misc,valid-type]
        ge = Decimal("11.0")

    class MyModel(BaseModel):
        conbytes_list_field: List[conbytes()]  # type: ignore[valid-type]
        condecimal_list_field: List[condecimal()]  # type: ignore[valid-type]
        confloat_list_field: List[confloat()]  # type: ignore[valid-type]
        conint_list_field: List[conint()]  # type: ignore[valid-type]
        conlist_list_field: List[conlist(str)]  # type: ignore[valid-type]
        conset_list_field: List[conset(str)]  # type: ignore[valid-type]
        constr_list_field: List[constr(to_lower=True)]  # type: ignore[valid-type]

        my_bytes_list_field: List[MyConstrainedBytes]
        my_decimal_list_field: List[MyConstrainedDecimal]
        my_float_list_field: List[MyConstrainedFloat]
        my_int_list_field: List[MyConstrainedInt]
        my_str_list_field: List[MyConstrainedString]

        my_bytes_dict_field: Dict[str, MyConstrainedBytes]
        my_decimal_dict_field: Dict[str, MyConstrainedDecimal]
        my_float_dict_field: Dict[str, MyConstrainedFloat]
        my_int_dict_field: Dict[str, MyConstrainedInt]
        my_str_dict_field: Dict[str, MyConstrainedString]

    class MyFactory(ModelFactory):
        __model__ = MyModel

    result = MyFactory.build()

    assert result.conbytes_list_field
    assert result.condecimal_list_field
    assert result.confloat_list_field
    assert result.conint_list_field
    assert result.conlist_list_field
    assert result.conset_list_field
    assert result.constr_list_field
    assert result.my_bytes_list_field
    assert result.my_decimal_list_field
    assert result.my_float_list_field
    assert result.my_int_list_field
    assert result.my_str_list_field
    assert result.my_bytes_dict_field
    assert result.my_decimal_dict_field
    assert result.my_float_dict_field
    assert result.my_int_dict_field
    assert result.my_str_dict_field


@pytest.mark.skipif(
    IS_PYDANTIC_V1 or sys.version_info < (3, 9),
    reason="pydantic 2 only test, does not work correctly in py 3.8",
)
def test_nested_constrained_attribute_handling_pydantic_2() -> None:
    # subclassing the constrained fields is not documented by pydantic,
    # but is supported apparently

    class MyModel(BaseModel):
        conbytes_list_field: List[conbytes()]  # type: ignore[valid-type]
        condecimal_list_field: List[condecimal()]  # type: ignore[valid-type]
        confloat_list_field: List[confloat()]  # type: ignore[valid-type]
        conint_list_field: List[conint()]  # type: ignore[valid-type]
        conlist_list_field: List[conlist(str)]  # type: ignore[valid-type]
        conset_list_field: List[conset(str)]  # type: ignore[valid-type]
        constr_list_field: List[constr(to_lower=True)]  # type: ignore[valid-type]

    class MyFactory(ModelFactory):
        __model__ = MyModel

    result = MyFactory.build()

    assert result.conbytes_list_field
    assert result.condecimal_list_field
    assert result.confloat_list_field
    assert result.conint_list_field
    assert result.conlist_list_field
    assert result.conset_list_field
    assert result.constr_list_field


@pytest.mark.skipif(
    IS_PYDANTIC_V1 or sys.version_info < (3, 9),
    reason="pydantic 2 only test, does not work correctly in py 3.8",
)
def test_constrained_attribute_parsing_pydantic_v2() -> None:
    class ConstrainedModel(BaseModel):
        conbytes_field: conbytes()  # type: ignore[valid-type]
        condecimal_field: condecimal()  # type: ignore[valid-type]
        confloat_field: confloat()  # type: ignore[valid-type]
        conint_field: conint()  # type: ignore[valid-type]
        conlist_field: conlist(str, min_length=5, max_length=10)  # type: ignore[valid-type]
        conset_field: conset(str, min_length=5, max_length=10)  # type: ignore[valid-type]
        confrozenset_field: confrozenset(str, min_length=5, max_length=10)  # type: ignore[valid-type]
        constr_field: constr(to_lower=True)  # type: ignore[valid-type]
        str_field1: str = Field(min_length=11)
        str_field2: str = Field(max_length=11)
        str_field3: str = Field(min_length=8, max_length=11, pattern=REGEX_PATTERN)
        int_field: int = Field(gt=1, multiple_of=5)
        float_field: float = Field(gt=100, lt=1000)
        decimal_field: Decimal = Field(ge=100, le=1000)
        list_field: List[str] = Field(min_length=1, max_length=10)
        optional_field: Optional[constr(min_length=1)]  # type: ignore[valid-type]

    class MyFactory(ModelFactory):
        __model__ = ConstrainedModel

    result = MyFactory.build()

    assert isinstance(result.conbytes_field, bytes)
    assert isinstance(result.conint_field, int)
    assert isinstance(result.confloat_field, float)
    assert isinstance(result.condecimal_field, Decimal)
    assert isinstance(result.conlist_field, list)
    assert isinstance(result.conset_field, set)
    assert isinstance(result.confrozenset_field, frozenset)
    assert isinstance(result.str_field1, str)
    assert isinstance(result.constr_field, str)
    assert len(result.conlist_field) >= 5
    assert len(result.conlist_field) <= 10
    assert len(result.conset_field) >= 5
    assert len(result.conset_field) <= 10
    assert len(result.confrozenset_field) >= 5
    assert len(result.confrozenset_field) <= 10
    assert result.constr_field.lower() == result.constr_field
    assert len(result.str_field1) >= 11
    assert len(result.str_field2) <= 11
    assert len(result.str_field3) >= 8
    assert len(result.str_field3) <= 11
    match = re.search(REGEX_PATTERN, result.str_field3)
    assert match
    assert match[0]
    assert result.int_field >= 1
    assert result.int_field % 5 == 0
    assert result.float_field > 100
    assert result.float_field < 1000
    assert result.decimal_field > 100
    assert result.decimal_field < 1000
    assert len(result.list_field) >= 1
    assert len(result.list_field) <= 10
    assert all(isinstance(r, str) for r in result.list_field)
    assert result.optional_field is None or len(result.optional_field) >= 1


@pytest.mark.skipif(IS_PYDANTIC_V1, reason="pydantic 2 only test")
def test_complex_constrained_attribute_parsing_pydantic_v2() -> None:
    class MyModel(BaseModel):
        conlist_with_model_field: conlist(Person, min_length=3)  # type: ignore[valid-type]
        conlist_with_complex_type: conlist(  # type: ignore[valid-type]
            Dict[str, Tuple[Person, Person, Person]],
            min_length=1,
        )

    class MyFactory(ModelFactory):
        __model__ = MyModel

    result = MyFactory.build()

    assert len(result.conlist_with_model_field) >= 3
    assert all(isinstance(v, Person) for v in result.conlist_with_model_field)
    assert result.conlist_with_complex_type
    assert isinstance(result.conlist_with_complex_type[0], dict)
    assert isinstance(next(iter(result.conlist_with_complex_type[0].values())), tuple)
    assert len(next(iter(result.conlist_with_complex_type[0].values()))) == 3
    assert all(isinstance(v, Person) for v in next(iter(result.conlist_with_complex_type[0].values())))


def test_annotated_children() -> None:
    class A(BaseModel):
        a: Dict[int, Annotated[str, MinLen(min_length=20)]]
        b: List[Annotated[int, Gt(gt=1000)]]
        c: Annotated[List[Annotated[int, Gt(gt=1000)]], MinLen(min_length=50)]
        d: Dict[int, Annotated[List[Annotated[str, MinLen(1)]], MinLen(1)]]

    AFactory = ModelFactory.create_factory(A)

    assert AFactory.build()
