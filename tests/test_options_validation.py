from typing import List, Optional

import pytest
from pydantic import BaseModel, Field

from polyfactory import ConfigurationException
from polyfactory.factories.pydantic_factory import ModelFactory
from tests.models import Person


def test_validates_model_is_set_on_definition_of_factory() -> None:
    with pytest.raises(ConfigurationException):

        class MyFactory(ModelFactory):
            pass


def test_validates_connection_in_create_sync() -> None:
    class MyFactory(ModelFactory):
        __model__ = Person

    with pytest.raises(ConfigurationException):
        MyFactory.create_sync()


def test_validates_connection_in_create_batch_sync() -> None:
    class MyFactory(ModelFactory):
        __model__ = Person

    with pytest.raises(ConfigurationException):
        MyFactory.create_batch_sync(2)


@pytest.mark.asyncio()
async def test_validates_connection_in_create_async() -> None:
    class MyFactory(ModelFactory):
        __model__ = Person

    with pytest.raises(ConfigurationException):
        await MyFactory.create_async()


@pytest.mark.asyncio()
async def test_validates_connection_in_create_batch_async() -> None:
    class MyFactory(ModelFactory):
        __model__ = Person

    with pytest.raises(ConfigurationException):
        await MyFactory.create_batch_async(2)


def test_factory_handling_of_optionals() -> None:
    class ModelWithOptionalValues(BaseModel):
        name: Optional[str]
        id: str
        complex: List[Optional[str]] = Field(min_items=1)  # type: ignore[call-arg]

    class FactoryWithNoneOptionals(ModelFactory):
        __model__ = ModelWithOptionalValues
        __random_seed__ = 1

    assert any(r.name is None for r in [FactoryWithNoneOptionals.build() for _ in range(10)])
    assert any(r.name is not None for r in [FactoryWithNoneOptionals.build() for _ in range(10)])
    assert all(r.id is not None for r in [FactoryWithNoneOptionals.build() for _ in range(10)])
    assert any(r.complex[0] is None for r in [FactoryWithNoneOptionals.build() for _ in range(10)])
    assert any(r.complex[0] is not None for r in [FactoryWithNoneOptionals.build() for _ in range(10)])

    class FactoryWithoutNoneOptionals(ModelFactory):
        __model__ = ModelWithOptionalValues
        __allow_none_optionals__ = False

    assert all(r.name is not None for r in [FactoryWithoutNoneOptionals.build() for _ in range(10)])
    assert all(r.id is not None for r in [FactoryWithoutNoneOptionals.build() for _ in range(10)])
    assert any(r.complex[0] is not None for r in [FactoryWithoutNoneOptionals.build() for _ in range(10)])
