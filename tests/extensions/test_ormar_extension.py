from datetime import datetime
from enum import Enum
from typing import Optional

import sqlalchemy
from databases import Database
from ormar import DateTime, ForeignKey, Integer, Model, String
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


class Job(Model):
    id: int = Integer(autoincrement=True, primary_key=True)
    person: Optional[Person] = ForeignKey(Person)
    name: str = String(max_length=20)

    class Meta(BaseMeta):
        pass


class PersonFactory(OrmarModelFactory):
    __model__ = Person


class JobFactory(OrmarModelFactory):
    __model__ = Job
    person = None


class JobWithPersonFactory(OrmarModelFactory):
    __model__ = Job
    person = PersonFactory


def test_person_factory():
    result = PersonFactory.build()

    assert result.id
    assert result.created_at
    assert result.updated_at
    assert result.mood


def test_job_factory():
    job_name: str = "Unemployed"
    result = JobFactory.build(name=job_name)

    assert result.id
    assert result.name == job_name
    assert not result.person


def test_job_with_person_factory():
    job_name: str = "Unemployed"
    result = JobWithPersonFactory.build(name=job_name)

    assert result.id
    assert result.name == job_name
    assert result.person
    assert isinstance(result.person, Person)
