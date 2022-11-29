from datetime import datetime
from enum import Enum
from uuid import uuid4

import pytest
from pydantic import UUID4

try:
    import sqlalchemy
    from databases import Database
    from ormar import UUID, DateTime
    from ormar import Enum as OrmarEnum
    from ormar import ForeignKey, Integer, Model, String, Text
    from sqlalchemy import func

    from pydantic_factories.extensions import OrmarModelFactory
except ImportError:
    pytest.skip(allow_module_level=True)

postgres_dsn = "postgresql+asyncpg://pydantic-factories:pydantic-factories@postgres:5432/pydantic-factories"

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
    mood: Mood = String(choices=Mood, max_length=20)  # type: ignore

    class Meta(BaseMeta):
        pass


class Job(Model):
    id: int = Integer(autoincrement=True, primary_key=True)
    person: Person = ForeignKey(Person)
    name: str = String(max_length=20)

    class Meta(BaseMeta):
        pass


class PersonFactory(OrmarModelFactory):
    __model__ = Person


class JobFactory(OrmarModelFactory):
    __model__ = Job


def test_person_factory() -> None:
    result = PersonFactory.build()

    assert result.id
    assert result.created_at
    assert result.updated_at
    assert result.mood


def test_job_factory() -> None:
    job_name: str = "Unemployed"
    result = JobFactory.build(name=job_name)

    assert result.id
    assert result.name == job_name
    assert result.person is not None


def test_model_creation_after_factory_build() -> None:
    # https://github.com/starlite-api/pydantic-factories/issues/128
    class TestModel(Model):
        class Meta(BaseMeta):
            pass

        id: UUID4 = UUID(primary_key=True, default=uuid4)
        text: str = Text()
        text2: str = Text(nullable=True)
        created_date: datetime = DateTime(default=datetime.now)
        mood: Mood = OrmarEnum(enum_class=Mood, default=Mood.HAPPY)

    class TestModelFactory(OrmarModelFactory):
        __model__ = TestModel

    TestModelFactory.build()
    TestModel(text="qwerty")
