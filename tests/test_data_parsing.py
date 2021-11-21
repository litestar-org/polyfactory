import re
from collections import deque
from datetime import date, datetime, time, timedelta
from decimal import Decimal
from enum import Enum
from ipaddress import (
    IPv4Address,
    IPv4Interface,
    IPv4Network,
    IPv6Address,
    IPv6Interface,
    IPv6Network,
)
from pathlib import Path
from typing import Callable, Dict, List, Tuple
from uuid import UUID

from pydantic import (
    UUID1,
    UUID3,
    UUID4,
    UUID5,
    AnyHttpUrl,
    AnyUrl,
    BaseModel,
    ByteSize,
    DirectoryPath,
    EmailStr,
    Field,
    FilePath,
    HttpUrl,
    IPvAnyAddress,
    IPvAnyInterface,
    IPvAnyNetwork,
    Json,
    NameEmail,
    NegativeFloat,
    NegativeInt,
    NonNegativeInt,
    NonPositiveFloat,
    PaymentCardNumber,
    PositiveFloat,
    PositiveInt,
    PostgresDsn,
    PyObject,
    RedisDsn,
    SecretBytes,
    SecretStr,
    StrictBool,
    StrictBytes,
    StrictFloat,
    StrictInt,
    StrictStr,
    conbytes,
    condecimal,
    confloat,
    conint,
    conlist,
    conset,
    constr,
)
from pydantic.color import Color

from pydantic_factories import ModelFactory
from tests.models import Person, PersonFactoryWithDefaults, Pet


def test_type_property_parsing():
    class MyModel(BaseModel):
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
        PyObject_pydantic_type: PyObject
        Color_pydantic_type: Color
        Json_pydantic_type: Json
        PaymentCardNumber_pydantic_type: PaymentCardNumber
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

    class MyFactory(ModelFactory):
        __model__ = MyModel

    result = MyFactory.build()

    for key in MyFactory.get_provider_map().keys():
        key_name = key.__name__ if hasattr(key, "__name__") else key._name
        if hasattr(result, f"{key_name}_field"):
            assert isinstance(getattr(result, f"{key_name}_field"), key)
        elif hasattr(result, f"{key_name}_pydantic_type"):
            assert getattr(result, f"{key_name}_pydantic_type") is not None


def test_constrained_property_parsing():
    pattern = r"(a|b|c)zz"

    class MyModel(BaseModel):
        conbytes_field: conbytes()
        condecimal_field: condecimal()
        confloat_field: confloat()
        conint_field: conint()
        conlist_field: conlist(str)
        conset_field: conset(str)
        constr_field: constr(to_lower=True)
        str_field1: str = Field(min_length=11)
        str_field2: str = Field(max_length=11)
        str_field3: str = Field(min_length=8, max_length=11, regex=pattern)
        int_field: int = Field(gt=1, multiple_of=5)
        float_field: float = Field(gt=100, lt=1000)
        decimal_field: Decimal = Field(ge=100, le=1000)
        list_field: List[str] = Field(min_items=1, max_items=10)
        constant_field: int = Field(const=True, default=100)

    class MyFactory(ModelFactory):
        __model__ = MyModel

    result = MyFactory.build()

    assert isinstance(result.conbytes_field, bytes)
    assert isinstance(result.conint_field, int)
    assert isinstance(result.confloat_field, float)
    assert isinstance(result.condecimal_field, Decimal)
    assert isinstance(result.conlist_field, list)
    assert isinstance(result.conset_field, set)
    assert isinstance(result.str_field1, str)
    assert isinstance(result.constr_field, str)
    assert result.constr_field.lower() == result.constr_field
    assert len(result.str_field1) >= 11
    assert len(result.str_field2) <= 11
    assert len(result.str_field3) >= 8
    assert len(result.str_field3) <= 11
    match = re.search(pattern, result.str_field3)
    assert match and match.group(0)
    assert result.int_field >= 1
    assert result.int_field % 5 == 0
    assert result.float_field > 100
    assert result.float_field < 1000
    assert result.decimal_field > 100
    assert result.decimal_field < 1000
    assert len(result.list_field) >= 1
    assert len(result.list_field) <= 10
    assert all([isinstance(r, str) for r in result.list_field])
    assert result.constant_field == 100


def test_complex_constrained_property_parsing():
    class MyModel(BaseModel):
        conlist_with_model_field: conlist(Person, min_items=3)
        conlist_with_complex_type: conlist(Dict[str, Tuple[Person, Person, Person]], min_items=1)

    class MyFactory(ModelFactory):
        __model__ = MyModel

    result = MyFactory.build()

    assert len(result.conlist_with_model_field) >= 3
    assert all([isinstance(v, Person) for v in result.conlist_with_model_field])
    assert result.conlist_with_complex_type
    assert isinstance(result.conlist_with_complex_type[0], dict)
    assert isinstance(list(result.conlist_with_complex_type[0].values())[0], tuple)
    assert len(list(result.conlist_with_complex_type[0].values())[0]) == 3
    assert all([isinstance(v, Person) for v in list(result.conlist_with_complex_type[0].values())[0]])


def test_enum_parsing():
    class MyStrEnum(str, Enum):
        FIRST_NAME = "Moishe Zuchmir"
        SECOND_NAME = "Hannah Arendt"

    class MyIntEnum(Enum):
        ONE_HUNDRED = 100
        TWO_HUNDRED = 200

    class MyModel(BaseModel):
        name: MyStrEnum
        worth: MyIntEnum

    class MyFactory(ModelFactory):
        __model__ = MyModel

    result = MyFactory.build()

    assert isinstance(result.name, MyStrEnum)
    assert isinstance(result.worth, MyIntEnum)


def test_callback_parsing():
    today = date.today()

    class MyModel(BaseModel):
        name: str
        birthday: date
        secret: Callable

    class MyFactory(ModelFactory):
        __model__ = MyModel

        name = lambda: "moishe zuchmir"  # noqa: E731
        birthday = lambda: today  # noqa: E731

    result = MyFactory.build()

    assert result.name == "moishe zuchmir"
    assert result.birthday == today
    assert callable(result.secret)


def test_alias_parsing():
    class MyModel(BaseModel):
        aliased_field: str = Field(alias="special_field")

    class MyFactory(ModelFactory):
        __model__ = MyModel

    assert isinstance(MyFactory.build().aliased_field, str)


def test_embedded_models_parsing():
    class MyModel(BaseModel):
        pet: Pet

    class MyFactory(ModelFactory):
        __model__ = MyModel

    result = MyFactory.build()
    assert isinstance(result.pet, Pet)


def test_embedded_factories_parsing():
    class MyModel(BaseModel):
        person: Person

    class MyFactory(ModelFactory):
        __model__ = MyModel
        person = PersonFactoryWithDefaults

    result = MyFactory.build()
    assert isinstance(result.person, Person)
