from __future__ import annotations

from datetime import date, datetime
from typing import TYPE_CHECKING, Any, Callable, Generic, TypeVar, Union

from polyfactory.exceptions import MissingDependencyException
from polyfactory.factories.base import BaseFactory
from polyfactory.field_meta import FieldMeta

try:
    from sqlalchemy import inspect, orm, types
    from sqlalchemy.dialects import mysql, postgresql
    from sqlalchemy.exc import NoInspectionAvailable
    from sqlalchemy.orm import InstanceState, Mapper
except ImportError as e:
    raise MissingDependencyException("sqlalchemy is not installed") from e

if TYPE_CHECKING:
    from typing_extensions import TypeGuard


T = TypeVar("T", bound=orm.DeclarativeBase)


class SQLAlchemyFactory(Generic[T], BaseFactory[T]):
    __is_base_factory__ = True

    @classmethod
    def get_sqlalchemy_types(cls) -> dict[Any, Callable[[], Any]]:
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
    def get_model_fields(cls) -> list[FieldMeta]:
        fields_meta: list[FieldMeta] = []

        types_override = cls.get_sqlalchemy_types()
        columns = cls.__model__.__table__.columns
        for name, column in columns.items():
            annotation: type = type(column.type) if type(column.type) in types_override else column.type.python_type
            if column.nullable:
                annotation = Union[annotation, None]  # type: ignore[assignment]
            fields_meta.append(
                FieldMeta.from_type(
                    annotation=annotation,
                    name=name,
                    random=cls.__random__,
                )
            )

        return fields_meta
