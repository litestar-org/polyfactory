from typing import Any

import pytest
from sqlalchemy import Column, FetchedValue, Integer, String, select
from sqlalchemy.engine import Engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from sqlalchemy.orm import Session
from sqlalchemy.orm.decl_api import DeclarativeMeta, registry

from polyfactory.factories.sqlalchemy_factory import SQLAlchemyFactory, SQLAlchemyPersistenceMethod
from tests.sqlalchemy_factory.models import Shape

_registry = registry()


class Base(metaclass=DeclarativeMeta):
    __abstract__ = True
    registry = _registry
    metadata = _registry.metadata


class SystemModel(Base):
    __tablename__ = "system_model"

    id: Any = Column(Integer, primary_key=True)
    label: Any = Column(String, nullable=False)
    version: Any = Column(String, system=True, server_default=FetchedValue(), nullable=False)


class SystemFactory(SQLAlchemyFactory[SystemModel]):
    __model__ = SystemModel
    __set_primary_key__ = False


_CREATE_TABLE = (
    "CREATE TABLE system_model (id INTEGER PRIMARY KEY, label TEXT NOT NULL, "
    "version TEXT GENERATED ALWAYS AS ('database-managed') VIRTUAL)"
)


def test_system_column_direct_orm_control(engine: Engine) -> None:
    # SQLite's generated column stands in for a database-managed system column.
    with engine.begin() as connection:
        connection.exec_driver_sql(_CREATE_TABLE)
    with Session(engine) as session:
        instance = SystemModel()
        instance.label = "direct"
        session.add(instance)
        session.commit()

        assert instance.id == 1
        assert instance.label == "direct"
        assert instance.version == "database-managed"


def test_system_column_build() -> None:
    instance = SystemFactory.build()

    assert isinstance(instance.label, str)
    assert isinstance(instance.version, str)
    assert SystemFactory.build(version="explicit").version == "explicit"


@pytest.mark.parametrize("batch", [False, True])
@pytest.mark.parametrize("factory_override", [False, True])
@pytest.mark.parametrize("persistence_method", list(SQLAlchemyPersistenceMethod))
def test_system_column_sync_persistence(
    engine: Engine, batch: bool, factory_override: bool, persistence_method: SQLAlchemyPersistenceMethod
) -> None:
    with engine.begin() as connection:
        connection.exec_driver_sql(_CREATE_TABLE)
    with Session(engine) as session:

        class Factory(SystemFactory):
            __session__ = session
            __persistence_method__ = persistence_method
            if factory_override:
                version = "factory override"

        instances = Factory.create_batch_sync(2, label="ordinary") if batch else [Factory.create_sync(label="ordinary")]

        assert session.scalars(select(SystemModel.id)).all() == list(range(1, len(instances) + 1))
        assert all(instance.label == "ordinary" for instance in instances)
        assert all(instance.version == "database-managed" for instance in instances)
        assert isinstance(Factory.build().version, str)


@pytest.mark.parametrize("batch", [False, True])
@pytest.mark.parametrize("factory_override", [False, True])
@pytest.mark.parametrize("persistence_method", list(SQLAlchemyPersistenceMethod))
async def test_system_column_async_persistence(
    async_engine: AsyncEngine, batch: bool, factory_override: bool, persistence_method: SQLAlchemyPersistenceMethod
) -> None:
    async with async_engine.begin() as connection:
        await connection.exec_driver_sql(_CREATE_TABLE)
    async with AsyncSession(async_engine) as session:

        class Factory(SystemFactory):
            __async_session__ = session
            __persistence_method__ = persistence_method
            if factory_override:
                version = "factory override"

        instances = (
            await Factory.create_batch_async(2, label="ordinary")
            if batch
            else [await Factory.create_async(label="ordinary")]
        )

        assert (await session.scalars(select(SystemModel.id))).all() == list(range(1, len(instances) + 1))
        assert all(instance.label == "ordinary" for instance in instances)
        assert all(instance.version == "database-managed" for instance in instances)
        assert isinstance(Factory.build().version, str)


def test_system_column_explicit_persistence_value(engine: Engine) -> None:
    with engine.begin() as connection:
        connection.exec_driver_sql(_CREATE_TABLE)
    with Session(engine) as session:

        class Factory(SystemFactory):
            __session__ = session

        with pytest.raises(OperationalError, match="cannot INSERT into generated column"):
            Factory.create_sync(version="explicit")


def test_computed_column_batch_sync_persistence(engine: Engine) -> None:
    with Session(engine) as session:

        class Factory(SQLAlchemyFactory[Shape]):
            __model__ = Shape
            __set_primary_key__ = False
            __session__ = session

        instances = Factory.create_batch_sync(2)

        assert len(instances) == 2
        assert all(instance.area == instance.side**2 for instance in instances)


async def test_computed_column_batch_async_persistence(async_engine: AsyncEngine) -> None:
    async with AsyncSession(async_engine) as session:

        class Factory(SQLAlchemyFactory[Shape]):
            __model__ = Shape
            __set_primary_key__ = False
            __async_session__ = session

        instances = await Factory.create_batch_async(2)

        assert len(instances) == 2
        assert all(instance.area == instance.side**2 for instance in instances)
