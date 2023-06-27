from datetime import datetime
from typing import Any, List
from uuid import UUID

import bson
import pytest
from bson import ObjectId

from polyfactory.decorators import post_generated

try:
    from odmantic import AIOEngine, EmbeddedModel, Model

    from polyfactory.factories.odmantic_odm_factory import OdmanticModelFactory
except ImportError:
    AIOEngine, EmbeddedModel, Model, OdmanticModelFactory = None, None, None, None  # type: ignore
    pytest.importorskip("odmantic")


class OtherEmbeddedDocument(EmbeddedModel):  # type: ignore
    name: str
    serial: UUID
    created_on: datetime
    bson_id: bson.ObjectId
    bson_int64: bson.Int64
    bson_dec128: bson.Decimal128
    bson_binary: bson.Binary


class MyEmbeddedDocument(EmbeddedModel):  # type: ignore
    name: str
    serial: UUID
    other_embedded_document: OtherEmbeddedDocument
    created_on: datetime
    bson_id: bson.ObjectId
    bson_int64: bson.Int64
    bson_dec128: bson.Decimal128
    bson_binary: bson.Binary


class MyModel(Model):  # type: ignore
    created_on: datetime
    bson_id: bson.ObjectId
    bson_int64: bson.Int64
    bson_dec128: bson.Decimal128
    bson_binary: bson.Binary
    name: str
    embedded: MyEmbeddedDocument
    embedded_list: List[MyEmbeddedDocument]


@pytest.fixture()
async def odmantic_engine(mongo_connection: Any) -> AIOEngine:
    return AIOEngine(client=mongo_connection, database=mongo_connection.db_name)


def test_handles_odmantic_models() -> None:
    class MyFactory(OdmanticModelFactory):
        __model__ = MyModel

    result = MyFactory.build()

    assert isinstance(result, MyModel)
    assert isinstance(result.id, bson.ObjectId)
    assert isinstance(result.created_on, datetime)
    assert isinstance(result.bson_id, bson.ObjectId)
    assert isinstance(result.bson_int64, bson.Int64)
    assert isinstance(result.bson_dec128, bson.Decimal128)
    assert isinstance(result.bson_binary, bson.Binary)
    assert isinstance(result.name, str)
    assert isinstance(result.embedded, MyEmbeddedDocument)
    assert isinstance(result.embedded_list, list)
    for item in result.embedded_list:
        assert isinstance(item, MyEmbeddedDocument)
        assert isinstance(item.name, str)
        assert isinstance(item.serial, UUID)
        assert isinstance(item.created_on, datetime)
        assert isinstance(item.bson_id, bson.ObjectId)
        assert isinstance(item.bson_int64, bson.Int64)
        assert isinstance(item.bson_dec128, bson.Decimal128)
        assert isinstance(item.bson_binary, bson.Binary)

        other = item.other_embedded_document
        assert isinstance(other, OtherEmbeddedDocument)
        assert isinstance(other.name, str)
        assert isinstance(other.serial, UUID)
        assert isinstance(other.created_on, datetime)
        assert isinstance(other.bson_id, bson.ObjectId)
        assert isinstance(other.bson_int64, bson.Int64)
        assert isinstance(other.bson_dec128, bson.Decimal128)
        assert isinstance(other.bson_binary, bson.Binary)


def test_post_generated_from_id() -> None:
    class MyFactory(OdmanticModelFactory):
        __model__ = MyModel

        @post_generated
        @classmethod
        def name(cls, id: ObjectId) -> str:
            return f"{cls.__faker__.name()} [{id.generation_time}]"

    MyFactory.build()
