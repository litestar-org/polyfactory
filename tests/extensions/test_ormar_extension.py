from datetime import datetime
from enum import Enum
from random import choice
from typing import Any, Type, ItemsView, Tuple, List, Dict

import pytest
import sqlalchemy
from databases import Database
from ormar import Model, DateTime, String, Integer
from pydantic.fields import ModelField
from sqlalchemy import func

from pydantic_factories import ModelFactory
from tests.conftest import postgres_dsn

database = Database(url=postgres_dsn, force_rollback=True)
metadata = sqlalchemy.MetaData()

CHOICES_FIELD_NAME = "__ormar_choices__"


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


class OrmarAsyncPersistenceHandler:
    async def save(self, data: Any) -> None:
        # wip
        pass


class OrmarModelFactory(ModelFactory[Model]):
    @classmethod
    def get_provider_map(cls):
        initial = super().get_provider_map()
        return initial | {
            # String: cls.handle_string
        }

    @classmethod
    def get_model_fields(cls, model: Type[Model]) -> ItemsView[str, ModelField]:
        """ Handle ormar fields, we have to access the fields in a raw fashion because choices are not recorded """
        ignored_field_names = [*list(dir(Model)), "Config", "Meta"]
        field_names = [name for name in dir(model) if not name.startswith("_") and name not in ignored_field_names]
        field_accessors = [getattr(model, field_name) for field_name in field_names]
        ormar_model_fields = [getattr(accessor, "_field") for accessor in field_accessors]
        model_fields = model.__fields__.values()

        output: Dict[str, ModelField] = {}
        for ormar_field in ormar_model_fields:
            model_field = [field for field in model_fields if field.name == ormar_field.name][0]
            if ormar_field.choices:
                setattr(model_field, CHOICES_FIELD_NAME, ormar_field.choices)
            output[ormar_field.name] = model_field
        return output.items()

    @classmethod
    def get_field_value(cls, field_name: str, model_field: ModelField) -> Any:
        """ handle ormar choices if any """
        if hasattr(model_field, CHOICES_FIELD_NAME):
            return choice(getattr(model_field, CHOICES_FIELD_NAME))
        return super().get_field_value(field_name=field_name, model_field=model_field)


class PersonFactory(OrmarModelFactory):
    __model__ = Person
    __async_persistence__ = OrmarAsyncPersistenceHandler


@pytest.mark.asyncio
async def test_person_factory():
    result = await PersonFactory.create_async()

    assert result
