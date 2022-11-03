from typing import Callable, List

import pytest

try:
    import pymongo
    from beanie import Document, Link, init_beanie
    from beanie.odm.fields import Indexed, PydanticObjectId
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
    id: PydanticObjectId
    name: str
    index: Indexed(str, pymongo.DESCENDING)  # type: ignore
    siblings: List[PydanticObjectId]


class MyOtherDocument(Document):
    id: PydanticObjectId
    document: Link[MyDocument]


class MyFactory(BeanieDocumentFactory):
    __model__ = MyDocument


class MyOtherFactory(BeanieDocumentFactory):
    __model__ = MyOtherDocument


@pytest.fixture()
async def beanie_init(mongo_connection: AsyncIOMotorClient):
    await init_beanie(database=mongo_connection.db_name, document_models=[MyDocument, MyOtherDocument])


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


@pytest.mark.asyncio()
async def test_beanie_links(beanie_init: Callable) -> None:
    result = await MyOtherFactory.create_async()
    assert isinstance(result.document, MyDocument)
