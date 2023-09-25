from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Type

import pytest
from sqlalchemy import Column, ForeignKey, Integer, String, create_engine, inspect, orm, types
from sqlalchemy.engine import Engine
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import Session
from sqlalchemy.orm.decl_api import DeclarativeMeta, registry

from polyfactory.exceptions import ConfigurationException
from polyfactory.factories.sqlalchemy_factory import SQLAlchemyFactory


@pytest.fixture()
def engine() -> Engine:
    return create_engine("sqlite:///:memory:")


@pytest.fixture()
def async_engine() -> AsyncEngine:
    return create_async_engine("sqlite+aiosqlite:///:memory:")


async def create_tables(engine: AsyncEngine, base: Type) -> None:
    async with engine.connect() as connection:
        await connection.run_sync(base.metadata.create_all)


_registry = registry()


class Base(metaclass=DeclarativeMeta):
    __abstract__ = True
    __allow_unmapped__ = True

    registry = _registry
    metadata = _registry.metadata


class Author(Base):
    __tablename__ = "authors"

    id: Any = Column(Integer(), primary_key=True)
    books: Any = orm.relationship(
        "Book",
        uselist=True,
        back_populates="author",
    )


class Book(Base):
    __tablename__ = "books"

    id: Any = Column(Integer(), primary_key=True)
    author_id: Any = Column(
        Integer(),
        ForeignKey(Author.id),
        nullable=False,
    )
    author: Any = orm.relationship(
        Author,
        uselist=False,
        back_populates="books",
    )


@dataclass
class NonSQLAchemyClass:
    id: int


@pytest.mark.parametrize(
    "invalid_model",
    (
        Base,
        NonSQLAchemyClass,
    ),
)
def test_invalid_model(invalid_model: type) -> None:
    with pytest.raises(ConfigurationException):
        SQLAlchemyFactory.create_factory(invalid_model)


def test_python_type_handling() -> None:
    _registry = registry()

    class Base(metaclass=DeclarativeMeta):
        __abstract__ = True

        registry = _registry
        metadata = _registry.metadata

    class Animal(str, Enum):
        DOG = "Dog"
        CAT = "Cat"

    class Model(Base):
        __tablename__ = "model"

        id: Any = Column(Integer(), primary_key=True)
        str_type: Any = Column(String(), nullable=False)
        enum_type: Any = Column(types.Enum(Animal), nullable=False)
        str_array_type: Any = Column(
            types.ARRAY(types.String),
            nullable=False,
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
def test_sqlalchemy_type_handlers(type_: types.TypeEngine) -> None:
    _registry = registry()

    class Base(metaclass=DeclarativeMeta):
        __abstract__ = True

        registry = _registry
        metadata = _registry.metadata

    class Model(Base):
        __tablename__ = "model_with_overriden_type"

        id: Any = Column(Integer(), primary_key=True)
        overridden: Any = Column(type_, nullable=False)

    class ModelFactory(SQLAlchemyFactory[Model]):
        __model__ = Model

    instance = ModelFactory.build()
    assert instance.overridden is not None


def test_optional_field() -> None:
    class Model(Base):
        __tablename__ = "model_with_optional_field"

        id: Any = Column(Integer(), primary_key=True)
        optional_field: Any = Column(String(), nullable=True)

    class ModelFactory(SQLAlchemyFactory[Model]):
        __model__ = Model
        __random_seed__ = 0

    result = ModelFactory.build()
    assert result.optional_field is None


@pytest.mark.parametrize("set_primary_key", (True, False))
def test_set_primary_key(set_primary_key: bool) -> None:
    class AuthorFactory(SQLAlchemyFactory[Author]):
        __model__ = Author
        __set_primary_key__ = set_primary_key

    result = AuthorFactory.build()
    assert bool(result.id) is set_primary_key


@pytest.mark.parametrize("set_foreign_keys", (True, False))
def test_set_foreign_keys(set_foreign_keys: bool) -> None:
    class BookFactory(SQLAlchemyFactory[Book]):
        __model__ = Book
        __set_foreign_keys__ = set_foreign_keys

    result = BookFactory.build()
    assert bool(result.author_id) is set_foreign_keys


def test_relationship_resolution() -> None:
    class BookFactory(SQLAlchemyFactory[Book]):
        __model__ = Book
        __set_relationships__ = True

    result = BookFactory.build()
    assert isinstance(result.author, Author)


def test_relationship_list_resolution() -> None:
    class AuthorFactory(SQLAlchemyFactory[Author]):
        __model__ = Author
        __set_relationships__ = True

    result = AuthorFactory.build()
    assert isinstance(result.books, list)
    assert isinstance(result.books[0], Book)


async def test_invalid_peristence_config_raises() -> None:
    class AuthorFactory(SQLAlchemyFactory[Author]):
        __model__ = Author

    with pytest.raises(
        ConfigurationException,
        match="A '__sync_persistence__' handler must be defined in the factory to use this method",
    ):
        AuthorFactory.create_sync()

    with pytest.raises(
        ConfigurationException,
        match="An '__async_persistence__' handler must be defined in the factory to use this method",
    ):
        await AuthorFactory.create_async()


@pytest.mark.parametrize(
    "session_config",
    (
        lambda session: session,
        lambda session: (lambda: session),
    ),
)
def test_sync_persistence(engine: Engine, session_config: Callable[[Session], Any]) -> None:
    Base.metadata.create_all(bind=engine)

    with Session(bind=engine) as session:

        class AuthorFactory(SQLAlchemyFactory[Author]):
            __session__ = session_config(session)
            __model__ = Author

        author = AuthorFactory.create_sync()
        assert author.id is not None
        assert inspect(author).persistent  # type: ignore[union-attr]

        batch_result = AuthorFactory.create_batch_sync(size=2)
        assert len(batch_result) == 2
        for batch_item in batch_result:
            assert inspect(batch_item).persistent  # type: ignore[union-attr]


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
    _registry = registry()

    class Base(metaclass=DeclarativeMeta):
        __abstract__ = True

        registry = _registry
        metadata = _registry.metadata

    class AsyncModel(Base):
        __tablename__ = "table"

        id: Any = Column(Integer(), primary_key=True)

    await create_tables(async_engine, Base)

    async with AsyncSession(async_engine) as session:

        class Factory(SQLAlchemyFactory[AsyncModel]):
            __async_session__ = session_config(session)
            __model__ = AsyncModel

        result = await Factory.create_async()
        assert inspect(result).persistent  # type: ignore[union-attr]

        batch_result = await Factory.create_batch_async(size=2)
        assert len(batch_result) == 2
        for batch_item in batch_result:
            assert inspect(batch_item).persistent  # type: ignore[union-attr]


def test_alias() -> None:
    class ModelWithAlias(Base):
        __tablename__ = "table"

        id: Any = Column(Integer(), primary_key=True)
        name: Any = Column("alias", String(), nullable=False)

    class ModelFactory(SQLAlchemyFactory[ModelWithAlias]):
        __model__ = ModelWithAlias

    result = ModelFactory.build()
    assert isinstance(result.name, str)
