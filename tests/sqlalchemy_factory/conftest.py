from collections.abc import AsyncIterator, Iterator

import pytest
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from tests.sqlalchemy_factory.models import Base


@pytest.fixture()
def engine() -> Iterator[Engine]:
    """Create a sync engine and clean up tables before and after each test."""
    _engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(_engine)
    try:
        yield _engine
    finally:
        Base.metadata.drop_all(_engine)
        _engine.dispose()


@pytest.fixture()
async def async_engine() -> AsyncIterator[AsyncEngine]:
    """Create an async engine and clean up tables before and after each test."""
    _engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    try:
        yield _engine
    finally:
        async with _engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        await _engine.dispose()
