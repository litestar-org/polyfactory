from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Type, Union
from uuid import UUID

import pytest
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    create_engine,
    func,
    inspect,
    orm,
    text,
    types,
)
from sqlalchemy.engine import Engine
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Session
from sqlalchemy.orm.decl_api import DeclarativeMeta, registry

from polyfactory.exceptions import ConfigurationException
from polyfactory.factories.base import BaseFactory
from polyfactory.factories.sqlalchemy_factory import SQLAlchemyFactory
from polyfactory.fields import Ignore


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
        collection_class=list,
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


def test_properties() -> None:
    _registry = registry()

    class Base(metaclass=DeclarativeMeta):
        __abstract__ = True

        registry = _registry
        metadata = _registry.metadata

    class Model(Base):
        __tablename__ = "model"

        id: Any = Column(Integer(), primary_key=True)
        age: Any = Column(Integer(), nullable=False)

        double_age = orm.column_property(age * 2)

        @hybrid_property
        def triple_age(self) -> int:
            return self.age * 3  # type: ignore[no-any-return]

    class ModelFactory(SQLAlchemyFactory[Model]): ...

    instance = ModelFactory.build()
    assert isinstance(instance, Model)
    # Expect empty as requires session to be set
    assert instance.double_age is None
    assert instance.age * 3 == instance.triple_age


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


def test_sqla_factory_create() -> None:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    class OverridenSQLAlchemyFactory(SQLAlchemyFactory):
        __is_base_factory__ = True
        __session__ = Session(engine)
        __set_relationships__ = True

    author: Author = OverridenSQLAlchemyFactory.create_factory(Author).create_sync()
    assert isinstance(author.books[0], Book)
    assert author.books[0].author is author

    book = OverridenSQLAlchemyFactory.create_factory(Book).create_sync()
    assert book.author is not None
    assert book.author.books == [book]

    BaseFactory._base_factories.remove(OverridenSQLAlchemyFactory)


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


@pytest.mark.parametrize(
    "session_config",
    (
        lambda session: session,
        lambda session: (lambda: session),
    ),
)
async def test_async_server_default_refresh(
    async_engine: AsyncEngine,
    session_config: Callable[[AsyncSession], Any],
) -> None:
    _registry = registry()

    class Base(metaclass=DeclarativeMeta):
        __abstract__ = True

        registry = _registry
        metadata = _registry.metadata

    class AsyncRefreshModel(Base):
        __tablename__ = "server_default_test"

        id: Any = Column(Integer(), primary_key=True)
        test_datetime: Any = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
        test_str: Any = Column(String, nullable=False, server_default=text("test_str"))
        test_int: Any = Column(Integer, nullable=False, server_default=text("123"))
        test_bool: Any = Column(Boolean, nullable=False, server_default=text("False"))

    await create_tables(async_engine, Base)

    async with AsyncSession(async_engine) as session:

        class Factory(SQLAlchemyFactory[AsyncRefreshModel]):
            __async_session__ = session_config(session)
            __model__ = AsyncRefreshModel
            test_datetime = Ignore()
            test_str = Ignore()
            test_int = Ignore()
            test_bool = Ignore()

        result = await Factory.create_async()
        assert inspect(result).persistent  # type: ignore[union-attr]
        assert result.test_datetime is not None
        assert isinstance(result.test_datetime, datetime)
        assert result.test_str == "test_str"
        assert result.test_int == 123
        assert result.test_bool is False


def test_alias() -> None:
    class ModelWithAlias(Base):
        __tablename__ = "table"

        id: Any = Column(Integer(), primary_key=True)
        name: Any = Column("alias", String(), nullable=False)

    class ModelFactory(SQLAlchemyFactory[ModelWithAlias]):
        __model__ = ModelWithAlias

    result = ModelFactory.build()
    assert isinstance(result.name, str)


@pytest.mark.parametrize("python_type_", (UUID, None))
def test_sqlalchemy_custom_type_from_type_decorator(python_type_: Union[type, None]) -> None:
    class CustomType(types.TypeDecorator):
        impl = types.CHAR(32)
        cache_ok = True

        if python_type_ is not None:

            @property
            def python_type(self) -> type:
                return python_type_

    class Base(metaclass=DeclarativeMeta):
        __abstract__ = True
        __allow_unmapped__ = True

        registry = _registry
        metadata = _registry.metadata

    class Model(Base):
        __tablename__ = f"model_with_custom_types_{python_type_}"

        id: Any = Column(Integer(), primary_key=True)
        custom_type: Any = Column(type_=CustomType(), nullable=False)

    class ModelFactory(SQLAlchemyFactory[Model]):
        __model__ = Model

    instance = ModelFactory.build()

    expected_type = python_type_ if python_type_ is not None else CustomType.impl.python_type
    assert isinstance(instance.custom_type, expected_type)
