import sys
from collections import Counter, deque
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
from typing import Callable, Dict, List, Optional, Set, Tuple
from uuid import UUID

import pytest
from typing_extensions import Annotated, TypeAlias

import pydantic
from pydantic import (
    UUID1,
    UUID3,
    UUID4,
    UUID5,
    VERSION,
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
)

from polyfactory.factories.pydantic_factory import _IS_PYDANTIC_V1, ModelFactory
from tests.models import PetFactory

IS_PYDANTIC_V1 = _IS_PYDANTIC_V1
IS_PYDANTIC_V2 = not _IS_PYDANTIC_V1


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
