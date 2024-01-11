from sys import version_info
from typing import Callable, List

import pymongo
import pytest

try:
    from beanie import Document, Link, init_beanie
    from beanie.odm.fields import Indexed, PydanticObjectId
    from mongomock_motor import AsyncMongoMockClient

    from polyfactory.factories.beanie_odm_factory import BeanieDocumentFactory
except ImportError:
    pytest.importorskip("beanie")

    BeanieDocumentFactory = None  # type: ignore
    Document = None  # type: ignore
    Link = None  # type: ignore
    init_beanie = None  # type: ignore
    Indexed = None  # type: ignore
    PydanticObjectId = None  # type: ignore


@pytest.fixture()
def mongo_connection() -> AsyncMongoMockClient:
    return AsyncMongoMockClient()


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
async def beanie_init(mongo_connection: AsyncMongoMockClient) -> None:
    await init_beanie(database=mongo_connection.db_name, document_models=[MyDocument, MyOtherDocument])


async def test_handling_of_beanie_types(beanie_init: Callable) -> None:
    result = MyFactory.build()
    assert result.name
    assert result.index
    assert isinstance(result.index, str)


async def test_beanie_persistence_of_single_instance(beanie_init: Callable) -> None:
    result = await MyFactory.create_async()
    assert result.id
    assert result.name
    assert result.index
    assert isinstance(result.index, str)


async def test_beanie_persistence_of_multiple_instances(beanie_init: Callable) -> None:
    result = await MyFactory.create_batch_async(size=3)
    assert len(result) == 3
    for instance in result:
        assert instance.id
        assert instance.name
        assert instance.index
        assert isinstance(instance.index, str)


@pytest.mark.skipif(version_info < (3, 11), reason="test isolation issues on lower versions")
async def test_beanie_links(beanie_init: Callable) -> None:
    result = await MyOtherFactory.create_async()
    assert isinstance(result.document, MyDocument)
