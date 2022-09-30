from typing import List, Optional

import pytest
from faker import Faker
from pydantic import BaseModel, Field

from pydantic_factories import ConfigurationError, ModelFactory
from tests.models import Pet


def test_allows_user_to_define_faker_instance() -> None:
    my_faker = Faker()
    setattr(my_faker, "__test__attr__", None)

    class MyFactory(ModelFactory):
        __model__ = Pet
        __faker__ = my_faker

    assert hasattr(MyFactory._get_faker(), "__test__attr__")


def test_validates_model_is_set_in_build() -> None:
    class MyFactory(ModelFactory):
        pass

    with pytest.raises(ConfigurationError):
        MyFactory.build()


def test_validates_model_is_set_in_batch() -> None:
    class MyFactory(ModelFactory):
        pass

    with pytest.raises(ConfigurationError):
        MyFactory.batch(2)


def test_validates_connection_in_create_sync() -> None:
    class MyFactory(ModelFactory):
        pass

    with pytest.raises(ConfigurationError):
        MyFactory.create_sync()


def test_validates_connection_in_create_batch_sync() -> None:
    class MyFactory(ModelFactory):
        pass

    with pytest.raises(ConfigurationError):
        MyFactory.create_batch_sync(2)


@pytest.mark.asyncio()
async def test_validates_connection_in_create_async() -> None:
    class MyFactory(ModelFactory):
        pass

    with pytest.raises(ConfigurationError):
        await MyFactory.create_async()


@pytest.mark.asyncio()
async def test_validates_connection_in_create_batch_async() -> None:
    class MyFactory(ModelFactory):
        pass

    with pytest.raises(ConfigurationError):
        await MyFactory.create_batch_async(2)


def test_factory_handling_of_optionals() -> None:
    class ModelWithOptionalValues(BaseModel):
        name: Optional[str]
        id: str
        complex: List[Optional[str]] = Field(min_items=1)

    class FactoryWithNoneOptionals(ModelFactory):
        __model__ = ModelWithOptionalValues

    FactoryWithNoneOptionals.seed_random(1)

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


def test_determine_results() -> None:
    class ModelWithOptionalValues(BaseModel):
        name: Optional[str]

    class FactoryWithNoneOptionals(ModelFactory):
        __model__ = ModelWithOptionalValues

    ModelFactory.seed_random(0)
    before_seeding = [FactoryWithNoneOptionals.build() for _ in range(10)]
    ModelFactory.seed_random(0)
    after_seeding = [FactoryWithNoneOptionals.build() for _ in range(10)]
    assert before_seeding == after_seeding
