from enum import Enum
from typing import Any, Callable, List, Type

import pytest
from sqlalchemy import ForeignKey, __version__, create_engine, inspect, orm, types
from sqlalchemy.engine import Engine
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine

from polyfactory.factories.sqlalchemy_factory import SQLAlchemyFactory

if __version__.startswith("1"):
    pytest.importorskip("SQLAlchemy", "2")


@pytest.fixture
def engine() -> Engine:
    return create_engine("sqlite:///:memory:")


@pytest.fixture
def async_engine() -> AsyncEngine:
    return create_async_engine("sqlite+aiosqlite:///:memory:")


async def create_tables(engine: AsyncEngine, base: Type) -> None:
    async with engine.connect() as connection:
        await connection.run_sync(base.metadata.create_all)


class Base(orm.DeclarativeBase):
    ...


class Author(Base):
    __tablename__ = "authors"

    id: orm.Mapped[int] = orm.mapped_column(primary_key=True)
    books: orm.Mapped[List["Book"]] = orm.relationship(
        "Book",
        uselist=True,
        back_populates="author",
    )


class Book(Base):
    __tablename__ = "books"

    id: orm.Mapped[int] = orm.mapped_column(primary_key=True)
    author_id: orm.Mapped[int] = orm.mapped_column(ForeignKey(Author.id))
    author: orm.Mapped[Author] = orm.relationship(
        Author,
        uselist=False,
        back_populates="books",
    )


def test_python_type_handling_v2() -> None:
    class Base(orm.DeclarativeBase):
        ...

    class Animal(str, Enum):
        DOG = "Dog"
        CAT = "Cat"

    class Model(Base):
        __tablename__ = "model"

        id: orm.Mapped[int] = orm.mapped_column(primary_key=True)
        str_type: orm.Mapped[str]
        enum_type: orm.Mapped[Animal]
        str_array_type: orm.Mapped[List[str]] = orm.mapped_column(
            type_=types.ARRAY(types.String),
        )

    class ModelFactory(SQLAlchemyFactory[Model]):
        __model__ = Model

    instance = ModelFactory.build()
    assert isinstance(instance.id, int)
    assert isinstance(instance.str_type, str)
    assert isinstance(instance.enum_type, Animal)
    assert isinstance(instance.str_array_type, list)
    assert isinstance(instance.str_array_type[0], str)


@pytest.mark.parametrize(
    "type_",
    tuple(SQLAlchemyFactory.get_sqlalchemy_types().keys()),
)
def test_sqlalchemy_type_handlers_v2(type_: types.TypeEngine) -> None:
    class Base(orm.DeclarativeBase):
        ...

    class Model(Base):
        __tablename__ = "model_with_overriden_type"

        id: orm.Mapped[int] = orm.mapped_column(primary_key=True)
        overridden: orm.Mapped[Any] = orm.mapped_column(type_=type_)

    class ModelFactory(SQLAlchemyFactory[Model]):
        __model__ = Model

    instance = ModelFactory.build()
    assert instance.overridden is not None


@pytest.mark.parametrize(
    "session_config",
    (
        lambda session: session,
        lambda session: (lambda: session),
    ),
)
async def test_async_persistence(
    async_engine: AsyncEngine,
    session_config: Callable[[AsyncSession], Any],
) -> None:
    from sqlalchemy.ext.asyncio import AsyncAttrs

    class Base(orm.DeclarativeBase):
        ...

    class AsyncModel(AsyncAttrs, Base):
        __tablename__ = "table"

        id: orm.Mapped[int] = orm.mapped_column(primary_key=True)

    await create_tables(async_engine, Base)

    async with AsyncSession(async_engine) as session:

        class Factory(SQLAlchemyFactory[AsyncModel]):
            __async_session__ = session_config(session)
            __model__ = AsyncModel

        result = await Factory.create_async()
        assert await result.awaitable_attrs.id is not None
        assert inspect(result).persistent

        batch_result = await Factory.create_batch_async(size=2)
        assert len(batch_result) == 2
        for batch_item in batch_result:
            assert inspect(batch_item).persistent
