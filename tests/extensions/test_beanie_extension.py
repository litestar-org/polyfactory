from typing import Callable, List

import pytest

try:
    import pymongo
    from beanie import Document, init_beanie
    from beanie.odm.fields import Indexed, PydanticObjectId  # noqa: TC002
    from motor.motor_asyncio import AsyncIOMotorClient

    from pydantic_factories.extensions import BeanieDocumentFactory
except ImportError:
    pytest.skip(allow_module_level=True)

# mongo can be run locally or using the docker-compose file at the repository's root

mongo_dsn = "mongodb://localhost:27017"


@pytest.fixture()
def mongo_connection() -> AsyncIOMotorClient:
    return AsyncIOMotorClient(mongo_dsn)


class MyDocument(Document):
    name: str
    index: Indexed(str, pymongo.DESCENDING)  # type: ignore
    siblings: List[PydanticObjectId]


class MyFactory(BeanieDocumentFactory[MyDocument]):
    __model__ = MyDocument


@pytest.fixture()
async def beanie_init(mongo_connection: AsyncIOMotorClient):  # noqa: PT004
    await init_beanie(database=mongo_connection.db_name, document_models=[MyDocument])


@pytest.mark.asyncio()
async def test_handling_of_beanie_types(beanie_init: Callable) -> None:
    result = MyFactory.build()
    assert result.name
    assert result.index
    assert isinstance(result.index, str)


@pytest.mark.asyncio()
async def test_beanie_persistence_of_single_instance(beanie_init: Callable) -> None:
    result = await MyFactory.create_async()
    assert result.id
    assert result.name
    assert result.index
    assert isinstance(result.index, str)


@pytest.mark.asyncio()
async def test_beanie_persistence_of_multiple_instances(beanie_init: Callable) -> None:
    result = await MyFactory.create_batch_async(size=3)
    assert len(result) == 3
    for instance in result:
        assert instance.id
        assert instance.name
        assert instance.index
        assert isinstance(instance.index, str)
