import os
from abc import ABC
from base64 import b64encode
from collections import deque
from datetime import date, datetime, time, timedelta
from decimal import Decimal
from ipaddress import (
    IPv4Address,
    IPv4Interface,
    IPv4Network,
    IPv6Address,
    IPv6Interface,
    IPv6Network,
)
from pathlib import Path
from random import uniform
from typing import Any, Callable, Generic, List, Optional, TypeVar
from uuid import NAMESPACE_DNS, UUID, uuid1, uuid3, uuid4, uuid5

from faker import Faker
from pydantic import (
    UUID1,
    UUID3,
    UUID4,
    UUID5,
    AnyHttpUrl,
    AnyUrl,
    BaseModel,
    ByteSize,
    ConstrainedBytes,
    ConstrainedDecimal,
    ConstrainedFloat,
    ConstrainedInt,
    ConstrainedList,
    ConstrainedSet,
    ConstrainedStr,
    DirectoryPath,
    EmailStr,
    FilePath,
    HttpUrl,
    IPvAnyAddress,
    IPvAnyInterface,
    IPvAnyNetwork,
    Json,
    NameEmail,
    NegativeFloat,
    NegativeInt,
    NonNegativeInt,
    NonPositiveFloat,
    PaymentCardNumber,
    PositiveFloat,
    PositiveInt,
    PostgresDsn,
    PyObject,
    RedisDsn,
    SecretBytes,
    SecretStr,
    StrictBool,
    StrictBytes,
    StrictFloat,
    StrictInt,
    StrictStr,
)
from pydantic.color import Color
from pydantic.fields import ModelField
from typing_extensions import Type

from pydantic_factories.constraints.numbers import (
    handle_constrained_decimal,
    handle_constrained_float,
    handle_constrained_int,
)
from pydantic_factories.constraints.strings import handle_constrained_string
from pydantic_factories.exceptions import ConfigurationError
from pydantic_factories.protocols import (
    AsyncPersistenceProtocol,
    SyncPersistenceProtocol,
)

T = TypeVar("T", bound=BaseModel)

default_faker = Faker()


class ModelFactory(ABC, Generic[T]):
    __model__: Type[T]
    __faker__: Optional[Faker]
    __sync_persistence__: Optional[SyncPersistenceProtocol[T]]
    __async_persistence__: Optional[AsyncPersistenceProtocol[T]]

    def __init__(self):
        if not hasattr(self, "__model__"):
            raise ConfigurationError("missing model class in factory Meta")

    @property
    def sync_persistence(self) -> Optional[SyncPersistenceProtocol[T]]:
        """Returns sync_persistence protocol if present"""
        if hasattr(self, "__sync_persistence__"):
            return self.__sync_persistence__
        return None

    @property
    def async_persistence(self) -> Optional[AsyncPersistenceProtocol[T]]:
        """Returns async_persistence protocol if present"""
        if hasattr(self, "__async_persistence__"):
            return self.__async_persistence__
        return None

    @property
    def faker(self) -> Faker:
        """Returns an instance of faker"""
        if hasattr(self, "__faker__") and self.__faker__:
            return self.__faker__
        return default_faker

    def get_provider_map(self) -> dict[Any, Callable]:
        """
        Returns a dictionary of <type>:<callable> values

        Note: this method is distinct to allow overriding
        """

        def create_bytes() -> bytes:
            return b64encode(self.faker.pystr().encode("utf-8"))

        def create_path() -> Path:
            return Path(os.path.realpath(__file__))

        return {
            # primitives
            float: self.faker.pyfloat,
            int: self.faker.pyint,
            bool: self.faker.pybool,
            str: self.faker.pystr,
            bytes: create_bytes,
            # built-in objects
            dict: self.faker.pydict,
            tuple: self.faker.pytuple,
            list: self.faker.pylist,
            set: self.faker.pyset,
            frozenset: self.faker.pylist,
            deque: self.faker.pylist,
            # standard library objects
            Path: create_path,
            Decimal: self.faker.pydecimal,
            UUID: self.faker.uuid4,
            # datetime
            datetime: self.faker.date_time_between,
            date: self.faker.date_this_decade,
            time: self.faker.time,
            timedelta: self.faker.time_delta,
            # ip addresses
            IPv4Address: self.faker.ipv4,
            IPv4Interface: self.faker.ipv4,
            IPv4Network: lambda: self.faker.ipv4(network=True),
            IPv6Address: self.faker.ipv6,
            IPv6Interface: self.faker.ipv6,
            IPv6Network: lambda: self.faker.ipv6(network=True),
            # pydantic specific
            ByteSize: self.faker.pyint,
            PositiveInt: self.faker.pyint,
            FilePath: create_path,
            NegativeFloat: lambda: uniform(-100, -1),
            NegativeInt: lambda: self.faker.pyint() * -1,
            PositiveFloat: self.faker.pyint,
            NonPositiveFloat: lambda: uniform(-100, 0),
            NonNegativeInt: self.faker.pyint,
            StrictInt: self.faker.pyint,
            StrictBool: self.faker.pybool,
            StrictBytes: create_bytes,
            StrictFloat: self.faker.pyfloat,
            StrictStr: self.faker.pystr,
            DirectoryPath: lambda: create_path().parent,
            EmailStr: self.faker.free_email,
            NameEmail: self.faker.free_email,
            PyObject: lambda: "decimal.Decimal",
            Color: self.faker.hex_color,
            Json: self.faker.json,
            PaymentCardNumber: self.faker.credit_card_number,
            AnyUrl: self.faker.url,
            AnyHttpUrl: self.faker.url,
            HttpUrl: self.faker.url,
            PostgresDsn: lambda: "postgresql://user:secret@localhost",
            RedisDsn: lambda: "redis://localhost:6379",
            UUID1: uuid1,
            UUID3: lambda: uuid3(NAMESPACE_DNS, self.faker.pystr()),
            UUID4: uuid4,
            UUID5: lambda: uuid5(NAMESPACE_DNS, self.faker.pystr()),
            SecretBytes: create_bytes,
            SecretStr: self.faker.pystr,
            IPvAnyAddress: self.faker.ipv4,
            IPvAnyInterface: self.faker.ipv4,
            IPvAnyNetwork: lambda: self.faker.ipv4(network=True),
        }

    def get_mock_value(self, field_type: Any) -> Any:
        """
        Returns a mock value corresponding to the types supported by pydantic
        see: https://pydantic-docs.helpmanual.io/usage/types/
        """
        if field_type is not None:
            handler = self.get_provider_map().get(field_type)
            if handler is not None:
                return handler()
        return None

    def handle_constrained_field(self, outer_field_type: Any) -> Any:
        """Handle the built-in pydantic constrained value field types"""
        if isinstance(outer_field_type, ConstrainedFloat):
            return handle_constrained_float(outer_field_type, self.faker)
        if isinstance(outer_field_type, ConstrainedInt):
            return handle_constrained_int(outer_field_type, self.faker)
        if isinstance(outer_field_type, ConstrainedStr):
            return handle_constrained_string(outer_field_type, self.faker)
        if isinstance(outer_field_type, ConstrainedDecimal):
            return handle_constrained_decimal(outer_field_type, self.faker)
        if isinstance(outer_field_type, ConstrainedBytes):
            raise NotImplementedError()
        if isinstance(outer_field_type, ConstrainedList):
            raise NotImplementedError()
        if isinstance(outer_field_type, ConstrainedSet):
            raise NotImplementedError()

    def get_field_value(self, field_name: str, model_field: ModelField) -> Any:
        """Returns a field value on the sub-class if existing, otherwise returns a mock value"""
        if hasattr(self, field_name):
            return getattr(self, field_name)

        outer_field_type = model_field.outer_type_
        inner_field_type = model_field.type_
        if isinstance(
            outer_field_type,
            (
                ConstrainedList,
                ConstrainedBytes,
                ConstrainedSet,
                ConstrainedDecimal,
                ConstrainedStr,
                ConstrainedFloat,
                ConstrainedInt,
            ),
        ):
            return self.handle_constrained_field(outer_field_type=outer_field_type)
        # this is a workaround for the following issue: https://github.com/samuelcolvin/pydantic/issues/3415
        field_type = (
            inner_field_type
            if inner_field_type != Any  # pylint: disable=comparison-with-callable
            else outer_field_type
        )
        return self.get_mock_value(field_type=field_type)

    def build(self, **kwargs) -> T:
        """builds an instance of the factory's Meta.model"""
        for field_name, model_field in self.__model__.__fields__.items():
            if field_name not in kwargs:
                kwargs.setdefault(field_name, self.get_field_value(field_name=field_name, model_field=model_field))
        return self.__model__(**kwargs)

    def batch(self, size: int, **kwargs) -> List[T]:
        """builds a batch of size n of the factory's Meta.model"""
        return [self.build(**kwargs) for _ in range(size)]

    def create_sync(self, **kwargs) -> T:
        """Build and persist a single model instance synchronously"""
        if not self.sync_persistence:
            raise ConfigurationError("An sync_persistence handler must be defined in the factory to use this method")
        instance = self.build(**kwargs)
        return self.sync_persistence.save(instance)

    def create_batch_sync(self, size: int, **kwargs) -> List[T]:
        """Build and persist a batch of n size model instances synchronously"""
        if not self.sync_persistence:
            raise ConfigurationError("An sync_persistence handler must be defined in the factory to use this method")
        batch = self.batch(size, **kwargs)
        return self.sync_persistence.save_many(batch)

    async def create_async(self, **kwargs) -> T:
        """Build and persist a single model instance asynchronously"""
        if not self.async_persistence:
            raise ConfigurationError("An async_persistence handler must be defined in the factory to use this method")
        instance = self.build(**kwargs)
        return await self.async_persistence.save(instance)

    async def create_batch_async(self, size: int, **kwargs) -> List[T]:
        """Build and persist a batch of n size model instances asynchronously"""
        if not self.async_persistence:
            raise ConfigurationError("An async_persistence handler must be defined in the factory to use this method")
        batch = self.batch(size, **kwargs)
        return await self.async_persistence.save_many(batch)
