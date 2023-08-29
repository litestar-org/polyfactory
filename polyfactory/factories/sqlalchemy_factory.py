from __future__ import annotations

from datetime import date, datetime
from typing import TYPE_CHECKING, Any, Callable, ClassVar, Generic, List, TypeVar, Union

from polyfactory.exceptions import MissingDependencyException
from polyfactory.factories.base import BaseFactory
from polyfactory.field_meta import FieldMeta

try:
    from sqlalchemy import Column, inspect, orm, types
    from sqlalchemy.dialects import mysql, postgresql
    from sqlalchemy.exc import NoInspectionAvailable
    from sqlalchemy.orm import InstanceState, Mapper
except ImportError as e:
    raise MissingDependencyException("sqlalchemy is not installed") from e

if TYPE_CHECKING:
    from typing_extensions import TypeGuard


T = TypeVar("T", bound=orm.DeclarativeBase)


class SQLAlchemyFactory(Generic[T], BaseFactory[T]):
    """Base factory for SQLAlchemy models."""

    __is_base_factory__ = True
    __resolve_primary_key__: ClassVar[bool] = True
    """Configuration to consider primary key columns as a field or not."""
    __resolve_foreign_keys__: ClassVar[bool] = True
    """Configuration to consider columns with foreign keys as a field or not."""
    __resolve_relationships__: ClassVar[bool] = False
    """Configuration to consider relationships property as a model field or not."""

    @classmethod
    def get_sqlalchemy_types(cls) -> dict[Any, Callable[[], Any]]:
        """Get mapping of types where column type."""
        return {
            types.TupleType: cls.__faker__.pytuple,
            mysql.YEAR: lambda: cls.__random__.randint(1901, 2155),
            postgresql.CIDR: lambda: cls.__faker__.ipv4(network=False),
            postgresql.DATERANGE: lambda: (cls.__faker__.past_date(), date.today()),  # noqa: DTZ011
            postgresql.INET: lambda: cls.__faker__.ipv4(network=True),
            postgresql.INT4RANGE: lambda: tuple(sorted([cls.__faker__.pyint(), cls.__faker__.pyint()])),
            postgresql.INT8RANGE: lambda: tuple(sorted([cls.__faker__.pyint(), cls.__faker__.pyint()])),
            postgresql.MACADDR: lambda: cls.__faker__.hexify(text="^^:^^:^^:^^:^^:^^", upper=True),
            postgresql.NUMRANGE: lambda: tuple(sorted([cls.__faker__.pyint(), cls.__faker__.pyint()])),
            postgresql.TSRANGE: lambda: (cls.__faker__.past_datetime(), datetime.now()),  # noqa: DTZ005
            postgresql.TSTZRANGE: lambda: (cls.__faker__.past_datetime(), datetime.now()),  # noqa: DTZ005
        }

    @classmethod
    def get_provider_map(cls) -> dict[Any, Callable[[], Any]]:
        providers_map = super().get_provider_map()
        providers_map.update(cls.get_sqlalchemy_types())
        return providers_map

    @classmethod
    def is_supported_type(cls, value: Any) -> TypeGuard[type[T]]:
        try:
            inspected = inspect(value)
        except NoInspectionAvailable:
            return False
        return isinstance(inspected, (Mapper, InstanceState))

    @classmethod
    def should_column_be_set(cls, column: Column) -> bool:
        if not cls.__resolve_primary_key__ and column.primary_key:
            return False

        if not cls.__resolve_foreign_keys__ and column.foreign_keys:
            return False

        return True

    @classmethod
    def get_type_from_column(cls, column: Column) -> type:
        column_type = type(column.type)
        if column_type in cls.get_sqlalchemy_types():
            annotation = column_type
        elif issubclass(column_type, types.ARRAY):
            annotation = List[column.type.item_type.python_type]  # type: ignore[access,unused-ignore] # add unused-ignore as not an error in mypy
        else:
            annotation = column.type.python_type

        if column.nullable:
            annotation = Union[annotation, None]  # type: ignore[assignment]

        return annotation

    @classmethod
    def get_model_fields(cls) -> list[FieldMeta]:
        fields_meta: list[FieldMeta] = []

        table = inspect(cls.__model__)
        for name, column in table.columns.items():
            if not cls.should_column_be_set(column):
                continue

            fields_meta.append(
                FieldMeta.from_type(
                    annotation=cls.get_type_from_column(column),
                    name=name,
                    random=cls.__random__,
                    randomize_collection_length=cls.__randomize_collection_length__,
                    min_collection_length=cls.__min_collection_length__,
                    max_collection_length=cls.__max_collection_length__,
                )
            )

        if cls.__resolve_relationships__:
            for name, relationship in table.relationships.items():
                class_ = relationship.entity.class_
                annotation = class_ if not relationship.uselist else List[class_]  # type: ignore[valid-type]
                fields_meta.append(
                    FieldMeta.from_type(
                        name=name,
                        annotation=annotation,
                        random=cls.__random__,
                        randomize_collection_length=cls.__randomize_collection_length__,
                        min_collection_length=cls.__min_collection_length__,
                        max_collection_length=cls.__max_collection_length__,
                    )
                )

        return fields_meta
