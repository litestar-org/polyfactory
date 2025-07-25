import warnings
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Any, Callable, get_args
from uuid import UUID

import pytest
from sqlalchemy import (
    Column,
    Integer,
    Numeric,
    String,
    inspect,
    orm,
    select,
    types,
)
from sqlalchemy.engine import Engine
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Session
from sqlalchemy.orm.decl_api import DeclarativeMeta, registry

from polyfactory.exceptions import ConfigurationException, ParameterException
from polyfactory.factories.base import BaseFactory
from polyfactory.factories.sqlalchemy_factory import SQLAlchemyFactory
from polyfactory.fields import Ignore
from tests.sqlalchemy_factory.models import (
    AsyncModel,
    AsyncRefreshModel,
    Author,
    Base,
    Book,
    NonSQLAchemyClass,
    _registry,
)


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
        __tablename__ = "model_with_overridden_type"

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
    assert result.books is not None
    assert isinstance(result.books, list)
    assert isinstance(result.books[0], Book)


def test_sqla_factory_create(engine: Engine) -> None:
    Base.metadata.create_all(engine)

    class OverriddenSQLAlchemyFactory(SQLAlchemyFactory):
        __is_base_factory__ = True
        __session__ = Session(engine)
        __set_relationships__ = True

    author: Author = OverriddenSQLAlchemyFactory.create_factory(Author).create_sync()
    assert isinstance(author.books[0], Book)
    assert author.books[0].author is author

    book = OverriddenSQLAlchemyFactory.create_factory(Book).create_sync()
    assert book.author is not None
    assert book.author.books == [book]

    BaseFactory._base_factories.remove(OverriddenSQLAlchemyFactory)


async def test_invalid_persistence_config_raises() -> None:
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
    async with AsyncSession(async_engine) as session:

        class Factory(SQLAlchemyFactory[AsyncModel]):
            __async_session__ = session_config(session)
            __model__ = AsyncModel

        instance = await Factory.create_async()
        batch_result = await Factory.create_batch_async(size=2)
        assert len(batch_result) == 2

    async with AsyncSession(async_engine) as session:
        result = await session.scalar(select(AsyncModel).where(AsyncModel.id == instance.id))
        assert result

        for batch_item in batch_result:
            result = await session.scalar(select(AsyncModel).where(AsyncModel.id == batch_item.id))
            assert result


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
    async with AsyncSession(async_engine) as session:

        class Factory(SQLAlchemyFactory[AsyncRefreshModel]):
            __async_session__ = session_config(session)
            __model__ = AsyncRefreshModel
            test_datetime = Ignore()
            test_str = Ignore()
            test_int = Ignore()
            test_bool = Ignore()

        instance = await Factory.create_async()

    async with AsyncSession(async_engine) as session:
        result = await session.scalar(select(AsyncRefreshModel).where(AsyncRefreshModel.id == instance.id))
        assert result
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
def test_sqlalchemy_custom_type_from_type_decorator(python_type_: type) -> None:
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


def test_constrained_types() -> None:
    _registry = registry()

    class Base(metaclass=DeclarativeMeta):
        __abstract__ = True
        __allow_unmapped__ = True

        registry = _registry
        metadata = _registry.metadata

    class Model(Base):
        __tablename__ = "constrained_model"

        id: Any = Column(Integer(), primary_key=True)
        constrained_string: Any = Column(String(length=1), nullable=False)
        constrained_nullable_string: Any = Column(String(length=1), nullable=True)
        constrained_number: Any = Column(
            Numeric(precision=2, scale=1),
            nullable=False,
        )
        constrained_nullable_number: Any = Column(
            Numeric(precision=2, scale=1),
            nullable=True,
        )

    class ModelFactory(SQLAlchemyFactory[Model]):
        __model__ = Model

    instance = ModelFactory.build()
    assert len(instance.constrained_string) <= 1
    assert instance.constrained_nullable_string is None or len(instance.constrained_nullable_string) <= 1

    constrained_number: Decimal = instance.constrained_number
    assert isinstance(constrained_number, Decimal)
    assert abs(len(constrained_number.as_tuple().digits) - abs(int(constrained_number.as_tuple().exponent))) <= 2


@pytest.mark.parametrize(
    "numeric",
    (
        Numeric(),
        Numeric(precision=4),
        Numeric(precision=4, scale=0),
        Numeric(precision=4, scale=2),
    ),
)
def test_numeric_field(numeric: Numeric) -> None:
    _registry = registry()

    class Base(metaclass=DeclarativeMeta):
        __abstract__ = True
        __allow_unmapped__ = True

        registry = _registry
        metadata = _registry.metadata

    class NumericModel(Base):
        __tablename__ = "numerics"

        id: Any = Column(Integer(), primary_key=True)
        numeric_field: Any = Column(numeric, nullable=False)

    class NumericModelFactory(SQLAlchemyFactory[NumericModel]): ...

    result = NumericModelFactory.get_model_fields()[1]
    assert result.annotation is Decimal or get_args(result.annotation)[0] is Decimal
    if constraints := result.constraints:
        assert constraints.get("max_digits") == numeric.precision
        assert constraints.get("decimal_places") == numeric.scale


def test_unsupported_type_engine() -> None:
    class Location(types.TypeEngine): ...

    _registry = registry()

    class Base(metaclass=DeclarativeMeta):
        __abstract__ = True
        __allow_unmapped__ = True

        registry = _registry
        metadata = _registry.metadata

    class Place(Base):
        __tablename__ = "numerics"

        id: Any = Column(Integer(), primary_key=True)
        numeric_field: Any = Column(Location, nullable=False)

    factory = SQLAlchemyFactory.create_factory(Place)
    with pytest.raises(
        ParameterException,
        match="Unsupported type engine: Location()",
    ):
        factory.build()


def test_check_deprecated_setting() -> None:
    with pytest.warns(DeprecationWarning, match=r"Use of deprecated default '__set_relationships__'"):

        class BookFactory(SQLAlchemyFactory[Book]): ...


def test_check_deprecated_default_overridden_no_deprecation() -> None:
    with warnings.catch_warnings():
        warnings.simplefilter("error")

        class BookFactory(SQLAlchemyFactory[Book]):
            __set_relationships__ = False
            __set_association_proxy__ = False
            __check_model__ = False
