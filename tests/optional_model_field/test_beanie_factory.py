from typing import Callable, List

import pymongo
import pytest

try:
    from beanie import Document, init_beanie
    from beanie.odm.fields import Indexed, PydanticObjectId
    from mongomock_motor import AsyncMongoMockClient

    from polyfactory.factories.beanie_odm_factory import BeanieDocumentFactory
except ImportError:
    pytest.importorskip("beanie")

    BeanieDocumentFactory = None  # type: ignore
    Document = None  # type: ignore
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


class MyFactory(BeanieDocumentFactory[MyDocument]):
    ...


@pytest.fixture()
async def beanie_init(mongo_connection: AsyncMongoMockClient) -> None:
    await init_beanie(database=mongo_connection.db_name, document_models=[MyDocument])  # type: ignore


async def test_handling_of_beanie_types(beanie_init: Callable) -> None:
    assert getattr(MyFactory, "__model__") is MyDocument
    result: MyDocument = MyFactory.build()
    assert result.name
    assert result.index
    assert isinstance(result.index, str)
