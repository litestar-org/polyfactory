from datetime import date
from enum import Enum
from typing import Callable, Literal, Optional

import pytest
from typing_extensions import TypeAlias

from pydantic import (
    AmqpDsn,
    AnyHttpUrl,
    AnyUrl,
    BaseConfig,
    BaseModel,
    HttpUrl,
    KafkaDsn,
    PostgresDsn,
    RedisDsn,
)

from polyfactory.exceptions import ParameterException
from polyfactory.factories.pydantic_factory import ModelFactory
from tests.models import Person, PersonFactoryWithDefaults, Pet


def test_enum_parsing() -> None:
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


def test_callback_parsing() -> None:
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


def test_literal_parsing() -> None:
    class MyModel(BaseModel):
        literal_field: "Literal['yoyos']"
        multi_literal_field: "Literal['nolos', 'zozos', 'kokos']"

    class MyFactory(ModelFactory):
        __model__ = MyModel

    assert MyFactory.build().literal_field == "yoyos"
    batch = MyFactory.batch(30)
    values = {v.multi_literal_field for v in batch}
    assert values == {"nolos", "zozos", "kokos"}


def test_embedded_models_parsing() -> None:
    class MyModel(BaseModel):
        pet: Pet

    class MyFactory(ModelFactory):
        __model__ = MyModel

    result = MyFactory.build()
    assert isinstance(result.pet, Pet)


def test_embedded_factories_parsing() -> None:
    class MyModel(BaseModel):
        person: Person

    class MyFactory(ModelFactory):
        __model__ = MyModel
        person = PersonFactoryWithDefaults

    result = MyFactory.build()
    assert isinstance(result.person, Person)


def test_class_parsing() -> None:
    class TestClassWithoutKwargs:
        def __init__(self) -> None:
            self.flag = "123"

    class MyModel(BaseModel):
        class Config(BaseConfig):
            arbitrary_types_allowed = True

        class_field: TestClassWithoutKwargs
        # just a few select exceptions, to verify this works
        exception_field: Exception
        type_error_field: TypeError
        attribute_error_field: AttributeError
        runtime_error_field: RuntimeError

    class MyFactory(ModelFactory):
        __model__ = MyModel

    result = MyFactory.build()

    assert isinstance(result.class_field, TestClassWithoutKwargs)
    assert result.class_field.flag == "123"
    assert isinstance(result.exception_field, Exception)
    assert isinstance(result.type_error_field, TypeError)
    assert isinstance(result.attribute_error_field, AttributeError)
    assert isinstance(result.runtime_error_field, RuntimeError)

    class TestClassWithKwargs:
        def __init__(self, _: str) -> None:
            self.flag = str

    class MyNewModel(BaseModel):
        class Config(BaseConfig):
            arbitrary_types_allowed = True

        class_field: TestClassWithKwargs

    class MySecondFactory(ModelFactory):
        __model__ = MyNewModel

    with pytest.raises(ParameterException):
        MySecondFactory.build()


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
