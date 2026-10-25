import pytest
from sqlalchemy import func, select
from sqlalchemy.engine import Engine
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from sqlalchemy.orm import Session

from polyfactory.factories.sqlalchemy_factory import (
    SQLAlchemyBuildContext,
    SQLAlchemyFactory,
    SQLAlchemyPersistenceMethod,
)
from tests.sqlalchemy_factory.models import Shape


@pytest.mark.parametrize("size", (0, 1, 3))
@pytest.mark.parametrize("persistence_method", tuple(SQLAlchemyPersistenceMethod))
def test_computed_column_batch_sync_persistence(
    engine: Engine, size: int, persistence_method: SQLAlchemyPersistenceMethod
) -> None:
    with Session(engine) as session:

        class ShapeFactory(SQLAlchemyFactory[Shape]):
            __session__ = session
            __persistence_method__ = persistence_method
            __set_primary_key__ = False

        build_context: SQLAlchemyBuildContext = {"seen_models": set(), "skip_computed_fields": False}
        instances = ShapeFactory.create_batch_sync(size, side=7, _build_context=build_context)

        assert build_context == {"seen_models": set(), "skip_computed_fields": False}
        assert len(instances) == size
        for instance in instances:
            assert instance.side == 7
            assert instance.area == 49
        assert session.query(Shape).count() == size
        assert ShapeFactory.build(side=7, area=12).area == 12


@pytest.mark.parametrize("size", (0, 1, 3))
@pytest.mark.parametrize("persistence_method", tuple(SQLAlchemyPersistenceMethod))
async def test_computed_column_batch_async_persistence(
    async_engine: AsyncEngine, size: int, persistence_method: SQLAlchemyPersistenceMethod
) -> None:
    async with AsyncSession(async_engine) as session:

        class ShapeFactory(SQLAlchemyFactory[Shape]):
            __async_session__ = session
            __persistence_method__ = persistence_method
            __set_primary_key__ = False

        build_context: SQLAlchemyBuildContext = {"seen_models": set(), "skip_computed_fields": False}
        instances = await ShapeFactory.create_batch_async(size, side=7, _build_context=build_context)

        assert build_context == {"seen_models": set(), "skip_computed_fields": False}
        assert len(instances) == size
        for instance in instances:
            assert instance.side == 7
            assert instance.area == 49
        assert await session.scalar(select(func.count()).select_from(Shape)) == size
        assert ShapeFactory.build(side=7, area=12).area == 12


def test_computed_column_batch_without_persistence(engine: Engine) -> None:
    with Session(engine) as session:

        class ShapeFactory(SQLAlchemyFactory[Shape]):
            __session__ = session

        instances = ShapeFactory.batch(3, side=7, area=12)

        assert len(instances) == 3
        assert all(instance.area == 12 for instance in instances)
        assert session.query(Shape).count() == 0
