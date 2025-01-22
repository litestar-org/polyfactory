from sys import version_info
from typing import List, Optional

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


class CoroutineFactory(BeanieDocumentFactory):
    __model__ = MyDocument

    @classmethod
    async def siblings(cls) -> List[Optional[PydanticObjectId]]:
        documents = await MyDocument.find_all().to_list()
        document_ids = [document.id for document in documents]
        return cls.__random__.sample(document_ids, k=3)


@pytest.fixture(autouse=True)
async def beanie_init(mongo_connection: AsyncMongoMockClient) -> None:
    await init_beanie(database=mongo_connection.db_name, document_models=[MyDocument, MyOtherDocument])


async def test_handling_of_beanie_types() -> None:
    result = MyFactory.build()
    assert result.name
    assert result.index
    assert isinstance(result.index, str)


async def test_beanie_persistence_of_single_instance() -> None:
    result = await MyFactory.create_async()
    assert result.id
    assert result.name
    assert result.index
    assert isinstance(result.index, str)


async def test_async_coroutine_field() -> None:
    await MyFactory.create_batch_async(size=5)
    document = await CoroutineFactory.create_async()
    assert len(document.siblings) == 3
    for id in document.siblings:
        document = await MyDocument.find(MyDocument.id == id).first_or_none()
        assert document


async def test_beanie_persistence_of_multiple_instances() -> None:
    result = await MyFactory.create_batch_async(size=3)
    assert len(result) == 3
    for instance in result:
        assert instance.id
        assert instance.name
        assert instance.index
        assert isinstance(instance.index, str)


@pytest.mark.skipif(version_info < (3, 11), reason="test isolation issues on lower versions")
async def test_beanie_links() -> None:
    result = await MyOtherFactory.create_async()
    assert isinstance(result.document, MyDocument)
