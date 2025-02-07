from __future__ import annotations

from beanie import Document, init_beanie
from beanie.odm.fields import PydanticObjectId
from mongomock_motor import AsyncMongoMockClient

from polyfactory.factories.beanie_odm_factory import BeanieDocumentFactory


class MyDocument(Document):
    name: str


class CoroutineDocument(Document):
    name: str
    siblings: list[PydanticObjectId | None]


class MyFactory(BeanieDocumentFactory):
    __model__ = MyDocument


class CoroutineFactory(BeanieDocumentFactory):
    __model__ = CoroutineDocument

    @classmethod
    async def siblings(cls) -> list[PydanticObjectId | None]:
        documents = await MyDocument.find_all().to_list()
        document_ids = [document.id for document in documents]
        return cls.__random__.sample(document_ids, k=3)


async def test_async_coroutine_field() -> None:
    client = AsyncMongoMockClient()
    await init_beanie(database=client.db_name, document_models=[MyDocument, CoroutineDocument])
    await MyFactory.create_batch_async(5)

    document = await CoroutineFactory.create_async()
    for id in document.siblings:
        document = await MyDocument.find(MyDocument.id == id).first_or_none()
        assert document
