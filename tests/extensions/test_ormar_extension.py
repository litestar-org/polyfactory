from datetime import datetime
from enum import Enum
from typing import Any

import ormar as ormar
import pytest
import sqlalchemy
from databases import Database
from sqlalchemy import func

from pydantic_factories import ModelFactory

database = Database(url='postgresql+asyncpg://username:password@127.0.0.1:5434/db', force_rollback=True)
metadata = sqlalchemy.MetaData()


class BaseMeta:
    metadata = metadata
    database = database


class Mood(str, Enum):
    HAPPY = 'happy'
    GRUMPY = 'grumpy'


class Person(ormar.Model):
    id: int = ormar.Integer(autoincrement=True, primary_key=True)
    created_at: datetime = ormar.DateTime(timezone=True, server_default=func.now())
    updated_at: datetime = ormar.DateTime(timezone=True, server_default=func.now(), onupdate=func.now())
    mood: Mood = ormar.String(choices=Mood, max_length=20)

    class Meta(BaseMeta):
        pass


class OrmarAsyncPersistenceHandler:

    async def save(self, data: Any) -> None:
        # wip
        pass


class OrmarModelFactory(ModelFactory):

    @classmethod
    def get_provider_map(cls):
        initial = super().get_provider_map()
        return initial | {
            # ormar.String: cls.handle_string
        }


class PersonFactory(OrmarModelFactory):
    __model__ = Person
    __async_persistence__ = OrmarAsyncPersistenceHandler


@pytest.mark.asyncio
async def test_person_factory():
    await PersonFactory.create_async()