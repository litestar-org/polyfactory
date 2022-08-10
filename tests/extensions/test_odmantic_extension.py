from typing import List
from uuid import UUID  # noqa: TC003

import pytest
from odmantic import AIOEngine, EmbeddedModel, Model

from pydantic_factories.extensions.odmantic_odm import OdmanticModelFactory


class OtherEmbeddedDocument(EmbeddedModel):
    name: str
    serial: UUID


class MyEmbeddedDocument(EmbeddedModel):
    name: str
    serial: UUID
    other_embedded_document: OtherEmbeddedDocument


class MyModel(Model):
    name: str
    embedded: MyEmbeddedDocument
    embedded_list: List[MyEmbeddedDocument]


@pytest.fixture()
async def odmantic_engine(mongo_connection) -> AIOEngine:
    return AIOEngine(motor_client=mongo_connection, database=mongo_connection.db_name)


def test_handles_odmantic_models():
    class MyFactory(OdmanticModelFactory):
        __model__ = MyModel

    result = MyFactory.build()

    assert result.name
    assert result.embedded
    assert result.embedded_list
