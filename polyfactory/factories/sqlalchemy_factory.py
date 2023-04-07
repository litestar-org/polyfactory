from __future__ import annotations

from datetime import date, datetime, time, timedelta
from typing import TYPE_CHECKING, Any, Callable, Generic, TypeVar
from uuid import UUID

from _decimal import Decimal

from polyfactory.exceptions import MissingDependencyException
from polyfactory.factories.base import BaseFactory

try:
    from sqlalchemy import inspect, orm, types
    from sqlalchemy.dialects import mssql, mysql, oracle, postgresql, sqlite
    from sqlalchemy.exc import NoInspectionAvailable
    from sqlalchemy.orm import InstanceState, Mapper
except ImportError as e:
    raise MissingDependencyException("sqlalchemy is not installed") from e

if TYPE_CHECKING:
    from typing_extensions import TypeGuard

    from polyfactory.field_meta import FieldMeta


T = TypeVar("T", bound=orm.DeclarativeBase)


class SQLAlchemyFactory(Generic[T], BaseFactory[T]):
    __is_base_factory__ = True

    @classmethod
    def get_provider_map(cls) -> dict[Any, Callable[[], Any]]:
        providers_map = super().get_provider_map()
        return {
            # types.Enum: self.handle_enum,
            # postgresql.ENUM: self.handle_enum,
            # mysql.ENUM: self.handle_enum,
            **providers_map,
            types.ARRAY: providers_map[list],
            types.BIGINT: providers_map[int],
            types.BINARY: providers_map[str],
            types.BLOB: providers_map[str],
            types.BOOLEAN: providers_map[bool],
            types.BigInteger: providers_map[int],
            types.Boolean: providers_map[bool],
            types.CHAR: providers_map[str],
            types.CLOB: providers_map[str],
            types.DATE: providers_map[date],
            types.DATETIME: providers_map[datetime],
            types.DECIMAL: providers_map[int],
            types.Date: providers_map[date],
            types.DateTime: providers_map[datetime],
            types.FLOAT: providers_map[int],
            types.Float: providers_map[int],
            types.INT: providers_map[int],
            types.INTEGER: providers_map[int],
            types.Integer: providers_map[int],
            types.Interval: providers_map[timedelta],
            types.JSON: providers_map[dict],
            types.LargeBinary: providers_map[str],
            types.NCHAR: providers_map[str],
            types.NUMERIC: providers_map[int],
            types.NVARCHAR: providers_map[str],
            types.Numeric: providers_map[int],
            types.REAL: providers_map[int],
            types.SMALLINT: providers_map[int],
            types.SmallInteger: providers_map[int],
            types.String: providers_map[str],
            types.TEXT: providers_map[str],
            types.TIME: providers_map[time],
            types.TIMESTAMP: providers_map[datetime],
            types.Text: providers_map[str],
            types.Time: providers_map[time],
            types.TupleType: cls.__faker__.pytuple,
            types.Unicode: providers_map[str],
            types.UnicodeText: providers_map[str],
            types.VARBINARY: providers_map[str],
            types.VARCHAR: providers_map[str],
            # mssql
            mssql.BIT: providers_map[bool],
            mssql.DATETIME2: providers_map[datetime],
            mssql.DATETIMEOFFSET: providers_map[datetime],
            mssql.IMAGE: providers_map[str],
            mssql.MONEY: providers_map[Decimal],
            mssql.NTEXT: providers_map[str],
            mssql.REAL: providers_map[int],
            mssql.SMALLDATETIME: providers_map[datetime],
            mssql.SMALLMONEY: providers_map[Decimal],
            mssql.SQL_VARIANT: providers_map[str],
            mssql.TIME: providers_map[time],
            mssql.TINYINT: providers_map[int],
            mssql.UNIQUEIDENTIFIER: providers_map[str],
            mssql.VARBINARY: providers_map[str],
            mssql.XML: providers_map[str],
            # mysql
            mysql.BIGINT: providers_map[int],
            mysql.BIT: providers_map[bool],
            mysql.CHAR: providers_map[str],
            mysql.DATETIME: providers_map[datetime],
            mysql.DECIMAL: providers_map[int],
            mysql.DOUBLE: providers_map[int],
            mysql.FLOAT: providers_map[int],
            mysql.INTEGER: providers_map[int],
            mysql.JSON: providers_map[dict],
            mysql.LONGBLOB: providers_map[str],
            mysql.LONGTEXT: providers_map[str],
            mysql.MEDIUMBLOB: providers_map[str],
            mysql.MEDIUMINT: providers_map[int],
            mysql.MEDIUMTEXT: providers_map[str],
            mysql.NCHAR: providers_map[str],
            mysql.NUMERIC: providers_map[int],
            mysql.NVARCHAR: providers_map[str],
            mysql.REAL: providers_map[int],
            mysql.SET: providers_map[set],
            mysql.SMALLINT: providers_map[int],
            mysql.TEXT: providers_map[str],
            mysql.TIME: providers_map[time],
            mysql.TIMESTAMP: providers_map[datetime],
            mysql.TINYBLOB: providers_map[str],
            mysql.TINYINT: providers_map[int],
            mysql.TINYTEXT: providers_map[str],
            mysql.VARCHAR: providers_map[str],
            mysql.YEAR: cls.__random__.randint(1901, 2155),  # type: ignore
            # oracle
            oracle.BFILE: providers_map[str],
            oracle.BINARY_DOUBLE: providers_map[int],
            oracle.BINARY_FLOAT: providers_map[int],
            oracle.DATE: providers_map[datetime],
            oracle.DOUBLE_PRECISION: providers_map[int],
            oracle.INTERVAL: providers_map[timedelta],
            oracle.LONG: providers_map[str],
            oracle.NCLOB: providers_map[str],
            oracle.NUMBER: providers_map[int],
            oracle.RAW: providers_map[str],
            oracle.VARCHAR2: providers_map[str],
            oracle.VARCHAR: providers_map[str],
            # postgresql
            postgresql.ARRAY: providers_map[list],
            postgresql.BIT: providers_map[bool],
            postgresql.BYTEA: providers_map[str],
            postgresql.CIDR: lambda: cls.__faker__.ipv4(network=False),
            postgresql.DATERANGE: lambda: (cls.__faker__.past_date(), date.today()),  # noqa: DTZ011
            postgresql.DOUBLE_PRECISION: providers_map[int],
            postgresql.HSTORE: providers_map[dict],
            postgresql.INET: lambda: cls.__faker__.ipv4(network=True),
            postgresql.INT4RANGE: lambda: tuple(sorted([cls.__faker__.pyint(), cls.__faker__.pyint()])),
            postgresql.INT8RANGE: lambda: tuple(sorted([cls.__faker__.pyint(), cls.__faker__.pyint()])),
            postgresql.INTERVAL: providers_map[timedelta],
            postgresql.JSON: providers_map[dict],
            postgresql.JSONB: providers_map[dict],
            postgresql.MACADDR: lambda: cls.__faker__.hexify(text="^^:^^:^^:^^:^^:^^", upper=True),
            postgresql.MONEY: providers_map[Decimal],
            postgresql.NUMRANGE: lambda: tuple(sorted([cls.__faker__.pyint(), cls.__faker__.pyint()])),
            postgresql.TIME: providers_map[time],
            postgresql.TIMESTAMP: providers_map[datetime],
            postgresql.TSRANGE: lambda: (cls.__faker__.past_datetime(), datetime.now()),  # noqa: DTZ005
            postgresql.TSTZRANGE: lambda: (cls.__faker__.past_datetime(), datetime.now()),  # noqa: DTZ005
            postgresql.UUID: providers_map[UUID],
            # sqlite
            sqlite.DATE: providers_map[date],
            sqlite.DATETIME: providers_map[datetime],
            sqlite.JSON: providers_map[dict],
            sqlite.TIME: providers_map[time],
        }

    @classmethod
    def is_supported_type(cls, value: Any) -> TypeGuard[type[T]]:
        try:
            inspected = inspect(value)
        except NoInspectionAvailable:
            return False
        return isinstance(inspected, (Mapper, InstanceState))

    @classmethod
    def get_model_fields(cls) -> list[FieldMeta]:
        # TODO
        raise NotImplementedError()
