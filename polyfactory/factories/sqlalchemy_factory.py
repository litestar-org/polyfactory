from __future__ import annotations

from datetime import date, datetime
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    ClassVar,
    Collection,
    Generic,
    Iterable,
    MutableMapping,
    Protocol,
    TypeVar,
    Union,
    cast,
)

from typing_extensions import Annotated

from polyfactory.exceptions import MissingDependencyException, ParameterException
from polyfactory.factories.base import BaseFactory, BuildContext
from polyfactory.field_meta import Constraints, FieldMeta
from polyfactory.persistence import AsyncPersistenceProtocol, SyncPersistenceProtocol
from polyfactory.utils.types import Frozendict

try:
    from sqlalchemy import ARRAY, Column, Numeric, String, inspect, types
    from sqlalchemy.dialects import mssql, mysql, postgresql, sqlite
    from sqlalchemy.exc import NoInspectionAvailable
    from sqlalchemy.ext.associationproxy import AssociationProxy
    from sqlalchemy.orm import InstanceState, Mapper
except ImportError as e:
    msg = "sqlalchemy is not installed"
    raise MissingDependencyException(msg) from e

if TYPE_CHECKING:
    from random import Random

    from sqlalchemy.ext.asyncio import AsyncSession
    from sqlalchemy.orm import Session
    from sqlalchemy.sql.type_api import TypeEngine
    from typing_extensions import TypeGuard


T = TypeVar("T")


class SQLAlchemyFieldMeta(FieldMeta):
    def __init__(
        self,
        *,
        name: str,
        annotation: type,
        random: Random | None = None,
        default: Any = ...,
        children: list[FieldMeta] | None = None,
        constraints: Constraints | None = None,
        collection_class: type[Collection[Any]] | Callable[[], Collection[Any]] | None = None,
    ) -> None:
        super().__init__(
            name=name,
            annotation=annotation,
            random=random,
            default=default,
            children=children,
            constraints=constraints,
        )
        self.collection_class = collection_class


class SQLASyncPersistence(SyncPersistenceProtocol[T]):
    def __init__(self, session: Session) -> None:
        """Sync persistence handler for SQLAFactory."""
        self.session = session

    def save(self, data: T) -> T:
        self.session.add(data)
        self.session.commit()
        return data

    def save_many(self, data: list[T]) -> list[T]:
        self.session.add_all(data)
        self.session.commit()
        return data


class SQLAASyncPersistence(AsyncPersistenceProtocol[T]):
    def __init__(self, session: AsyncSession) -> None:
        """Async persistence handler for SQLAFactory."""
        self.session = session

    async def save(self, data: T) -> T:
        async with self.session as session:
            session.add(data)
            await session.commit()
            await session.refresh(data)
        return data

    async def save_many(self, data: list[T]) -> list[T]:
        async with self.session as session:
            session.add_all(data)
            await session.commit()
            for batch_item in data:
                await session.refresh(batch_item)
        return data


_T_co = TypeVar("_T_co", covariant=True)


class _SessionMaker(Protocol[_T_co]):
    @staticmethod
    def __call__() -> _T_co: ...


class SQLAlchemyFactory(Generic[T], BaseFactory[T]):
    """Base factory for SQLAlchemy models."""

    __is_base_factory__ = True

    __set_primary_key__: ClassVar[bool] = True
    """Configuration to consider primary key columns as a field or not."""
    __set_foreign_keys__: ClassVar[bool] = True
    """Configuration to consider columns with foreign keys as a field or not."""
    __set_relationships__: ClassVar[bool] = True
    """Configuration to consider relationships property as a model field or not."""
    __set_association_proxy__: ClassVar[bool] = True
    """Configuration to consider AssociationProxy property as a model field or not."""

    __session__: ClassVar[Session | _SessionMaker[Session] | None] = None
    __async_session__: ClassVar[AsyncSession | _SessionMaker[AsyncSession] | None] = None

    __config_keys__ = (
        *BaseFactory.__config_keys__,
        "__set_primary_key__",
        "__set_foreign_keys__",
        "__set_relationships__",
        "__set_association_proxy__",
    )

    @classmethod
    def get_sqlalchemy_types(cls) -> dict[Any, Callable[[], Any]]:
        """Get mapping of types where column type should be used directly.

        For sqlalchemy dialect `JSON` type, accepted only basic types in pydict in case sqlalchemy process `JSON` raise serialize error.
        """
        return {
            types.TupleType: cls.__faker__.pytuple,
            mssql.JSON: lambda: cls.__faker__.pydict(value_types=(str, int, bool, float)),
            mysql.YEAR: lambda: cls.__random__.randint(1901, 2155),
            mysql.JSON: lambda: cls.__faker__.pydict(value_types=(str, int, bool, float)),
            postgresql.CIDR: lambda: cls.__faker__.ipv4(network=True),
            postgresql.DATERANGE: lambda: (cls.__faker__.past_date(), date.today()),  # noqa: DTZ011
            postgresql.INET: lambda: cls.__faker__.ipv4(network=False),
            postgresql.INT4RANGE: lambda: tuple(sorted([cls.__faker__.pyint(), cls.__faker__.pyint()])),
            postgresql.INT8RANGE: lambda: tuple(sorted([cls.__faker__.pyint(), cls.__faker__.pyint()])),
            postgresql.MACADDR: lambda: cls.__faker__.hexify(text="^^:^^:^^:^^:^^:^^", upper=True),
            postgresql.NUMRANGE: lambda: tuple(sorted([cls.__faker__.pyint(), cls.__faker__.pyint()])),
            postgresql.TSRANGE: lambda: (cls.__faker__.past_datetime(), datetime.now()),  # noqa: DTZ005
            postgresql.TSTZRANGE: lambda: (cls.__faker__.past_datetime(), datetime.now()),  # noqa: DTZ005
            postgresql.HSTORE: lambda: cls.__faker__.pydict(value_types=(str, int, bool, float)),
            postgresql.JSON: lambda: cls.__faker__.pydict(value_types=(str, int, bool, float)),
            postgresql.JSONB: lambda: cls.__faker__.pydict(value_types=(str, int, bool, float)),
            sqlite.JSON: lambda: cls.__faker__.pydict(value_types=(str, int, bool, float)),
            types.JSON: lambda: cls.__faker__.pydict(value_types=(str, int, bool, float)),
        }

    @classmethod
    def get_sqlalchemy_constraints(cls) -> dict[type[TypeEngine], dict[str, str]]:
        """Get mapping of SQLA type engine to attribute to constraints key."""
        return {
            String: {
                "length": "max_length",
            },
            Numeric: {
                "precision": "max_digits",
                "scale": "decimal_places",
            },
        }

    @classmethod
    def get_provider_map(cls) -> dict[Any, Callable[[], Any]]:
        providers_map = super().get_provider_map()
        providers_map.update(cls.get_sqlalchemy_types())
        return providers_map

    @classmethod
    def get_field_value(
        cls,
        field_meta: FieldMeta,
        field_build_parameters: Any | None = None,
        build_context: BuildContext | None = None,
    ) -> Any:
        field_meta = cast("SQLAlchemyFieldMeta", field_meta)
        result = super().get_field_value(field_meta, field_build_parameters, build_context)

        if collection_class := field_meta.collection_class:
            collection = collection_class() if callable(collection_class) else collection_class
            items = result if isinstance(result, Iterable) else [result]

            keyfunc = getattr(collection, "keyfunc", None)
            if callable(keyfunc):
                mapping_collection = cast("MutableMapping[Any, Any]", collection)
                for item in items:
                    mapping_collection[keyfunc(item)] = item
                collection = mapping_collection
            else:
                extend = getattr(collection, "extend", None)
                if callable(extend):
                    extend(items)
                else:
                    append = getattr(collection, "append", None)
                    if callable(append):
                        for item in items:
                            append(item)
                    else:
                        add = getattr(collection, "add", None)
                        if callable(add):
                            for item in items:
                                add(item)

            return collection if collection is not None else result

        return result

    @classmethod
    def is_supported_type(cls, value: Any) -> TypeGuard[type[T]]:
        try:
            inspected = inspect(value)
        except NoInspectionAvailable:
            return False
        return isinstance(inspected, (Mapper, InstanceState))

    @classmethod
    def should_column_be_set(cls, column: Any) -> bool:
        if not isinstance(column, Column):
            return False

        if not cls.__set_primary_key__ and column.primary_key:
            return False

        return bool(cls.__set_foreign_keys__ or not column.foreign_keys)

    @classmethod
    def _get_type_from_type_engine(cls, type_engine: TypeEngine) -> type:
        if type(type_engine) in cls.get_sqlalchemy_types():
            return type(type_engine)

        annotation: type
        try:
            annotation = type_engine.python_type
        except NotImplementedError:
            if not hasattr(type_engine, "impl"):
                msg = f"Unsupported type engine: {type_engine}.\nOverride get_sqlalchemy_types to support"
                raise ParameterException(msg) from None
            annotation = type_engine.impl.python_type  # pyright: ignore[reportAttributeAccessIssue]

        constraints: Constraints = {}
        for type_, constraint_fields in cls.get_sqlalchemy_constraints().items():
            if not isinstance(type_engine, type_):
                continue
            for sqlalchemy_field, constraint_field in constraint_fields.items():
                if (value := getattr(type_engine, sqlalchemy_field, None)) is not None:
                    constraints[constraint_field] = value  # type: ignore[literal-required]
        if constraints:
            annotation = Annotated[annotation, Frozendict(constraints)]  # type: ignore[assignment]

        return annotation

    @classmethod
    def get_type_from_column(cls, column: Column) -> type:
        annotation: type
        if isinstance(column.type, (ARRAY, postgresql.ARRAY)):
            item_type = cls._get_type_from_type_engine(column.type.item_type)
            annotation = list[item_type]  # type: ignore[valid-type]
        else:
            annotation = cls._get_type_from_type_engine(column.type)

        if column.nullable:
            annotation = Union[annotation, None]  # type: ignore[assignment]

        return annotation

    @classmethod
    def get_model_fields(cls) -> list[FieldMeta]:
        fields_meta: list[FieldMeta] = []

        table: Mapper = inspect(cls.__model__)  # type: ignore[assignment]
        fields_meta.extend(
            SQLAlchemyFieldMeta.from_type(
                annotation=cls.get_type_from_column(column),
                name=name,
            )
            for name, column in table.columns.items()
            if cls.should_column_be_set(column)
        )
        if cls.__set_relationships__:
            for name, relationship in table.relationships.items():
                class_ = relationship.entity.class_
                annotation = class_ if not relationship.uselist else list[class_]  # type: ignore[valid-type]
                field_meta = SQLAlchemyFieldMeta.from_type(
                    name=name,
                    annotation=annotation,
                )
                field_meta.collection_class = relationship.collection_class
                fields_meta.append(field_meta)
        if cls.__set_association_proxy__:
            for name, attr in table.all_orm_descriptors.items():
                if isinstance(attr, AssociationProxy):
                    target_collection = table.relationships.get(attr.target_collection)
                    if target_collection:
                        target_class = target_collection.entity.class_
                        target_attr = getattr(target_class, attr.value_attr)
                        if target_attr:
                            class_ = target_attr.entity.class_
                            annotation = class_ if not target_collection.uselist else list[class_]  # type: ignore[valid-type]
                            fields_meta.append(
                                SQLAlchemyFieldMeta.from_type(
                                    name=name,
                                    annotation=annotation,
                                )
                            )

        return fields_meta

    @classmethod
    def _get_sync_persistence(cls) -> SyncPersistenceProtocol[T]:
        if cls.__session__ is not None:
            return (
                SQLASyncPersistence(cls.__session__())
                if callable(cls.__session__)
                else SQLASyncPersistence(cls.__session__)
            )
        return super()._get_sync_persistence()

    @classmethod
    def _get_async_persistence(cls) -> AsyncPersistenceProtocol[T]:
        if cls.__async_session__ is not None:
            return (
                SQLAASyncPersistence(cls.__async_session__())
                if callable(cls.__async_session__)
                else SQLAASyncPersistence(cls.__async_session__)
            )
        return super()._get_async_persistence()
