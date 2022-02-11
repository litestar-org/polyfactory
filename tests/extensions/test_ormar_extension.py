from datetime import datetime
from enum import Enum

import sqlalchemy
from databases import Database
from ormar import DateTime, Integer, Model, String
from sqlalchemy import func

from pydantic_factories.extensions import OrmarModelFactory
from tests.conftest import postgres_dsn

database = Database(url=postgres_dsn, force_rollback=True)
metadata = sqlalchemy.MetaData()


class BaseMeta:
    metadata = metadata
    database = database


class Mood(str, Enum):
    HAPPY = "happy"
    GRUMPY = "grumpy"


class Person(Model):
    id: int = Integer(autoincrement=True, primary_key=True)
    created_at: datetime = DateTime(timezone=True, server_default=func.now())
    updated_at: datetime = DateTime(timezone=True, server_default=func.now(), onupdate=func.now())
    mood: Mood = String(choices=Mood, max_length=20)

    class Meta(BaseMeta):
        pass


class PersonFactory(OrmarModelFactory):
    __model__ = Person


def test_person_factory():
    result = PersonFactory.build()

    assert result.id
    assert result.created_at
    assert result.updated_at
    assert result.mood
