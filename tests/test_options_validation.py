import pytest

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
