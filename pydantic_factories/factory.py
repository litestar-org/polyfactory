import os
from abc import ABC
from collections import deque
from datetime import date, datetime, time, timedelta
from decimal import Decimal
from enum import EnumMeta
from ipaddress import (
    IPv4Address,
    IPv4Interface,
    IPv4Network,
    IPv6Address,
    IPv6Interface,
    IPv6Network,
)
from pathlib import Path
from random import choice, uniform
from typing import Any, Callable, Dict, Generic, List, Optional, TypeVar, cast
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
from pydantic_factories.constraints.objects import (
    handle_constrained_list,
    handle_constrained_set,
)
from pydantic_factories.constraints.strings import (
    handle_constrained_bytes,
    handle_constrained_string,
)
from pydantic_factories.exceptions import ConfigurationError, ParameterError
from pydantic_factories.protocols import (
    AsyncPersistenceProtocol,
    SyncPersistenceProtocol,
)
from pydantic_factories.utils import create_random_bytes, inherits_from

T = TypeVar("T", bound=BaseModel)

default_faker = Faker()


class ModelFactory(ABC, Generic[T]):
    __model__: Type[T]
    __faker__: Optional[Faker]
    __sync_persistence__: Optional[SyncPersistenceProtocol[T]]
    __async_persistence__: Optional[AsyncPersistenceProtocol[T]]

    @classmethod
    def get_model_model(cls) -> Type[T]:
        """
        Returns the factory's model
        """
        if not hasattr(cls, "__model__") or not cls.__model__:
            raise ConfigurationError("missing model class in factory Meta")
        return cls.__model__

    @classmethod
    def get_sync_persistence(cls) -> SyncPersistenceProtocol[T]:
        """
        Returns a sync_persistence interface if present
        """
        if hasattr(cls, "__sync_persistence__") and cls.__sync_persistence__:
            return cls.__sync_persistence__
        raise ConfigurationError("A sync_persistence handler must be defined in the factory to use this method")

    @classmethod
    def get_async_persistence(cls) -> AsyncPersistenceProtocol[T]:
        """
        Returns an async_persistence interface
        """
        if hasattr(cls, "__async_persistence__") and cls.__async_persistence__:
            return cls.__async_persistence__
        raise ConfigurationError("An async_persistence handler must be defined in the factory to use this method")

    @classmethod
    def get_faker(cls) -> Faker:
        """
        Returns an instance of faker
        """
        if hasattr(cls, "__faker__") and cls.__faker__:
            return cls.__faker__
        return default_faker

    @classmethod
    def get_provider_map(cls) -> Dict[Any, Callable]:
        """
        Returns a dictionary of <type>:<callable> values

        Note: this method is distinct to allow overriding
        """

        def create_path() -> Path:
            return Path(os.path.realpath(__file__))

        def create_generic_fn() -> Callable:
            return lambda *args: None

        faker = cls.get_faker()

        return {
            # primitives
            float: faker.pyfloat,
            int: faker.pyint,
            bool: faker.pybool,
            str: faker.pystr,
            bytes: create_random_bytes,
            # built-in objects
            dict: faker.pydict,
            tuple: faker.pytuple,
            list: faker.pylist,
            set: faker.pyset,
            frozenset: lambda: frozenset(faker.pylist()),
            deque: lambda: deque(faker.pylist()),
            # standard library objects
            Path: create_path,
            Decimal: faker.pydecimal,
            UUID: uuid4,
            # datetime
            datetime: faker.date_time_between,
            date: faker.date_this_decade,
            time: faker.time,
            timedelta: faker.time_delta,
            # ip addresses
            IPv4Address: faker.ipv4,
            IPv4Interface: faker.ipv4,
            IPv4Network: lambda: faker.ipv4(network=True),
            IPv6Address: faker.ipv6,
            IPv6Interface: faker.ipv6,
            IPv6Network: lambda: faker.ipv6(network=True),
            # types
            Callable: create_generic_fn,
            # pydantic specific
            ByteSize: faker.pyint,
            PositiveInt: faker.pyint,
            FilePath: create_path,
            NegativeFloat: lambda: uniform(-100, -1),
            NegativeInt: lambda: faker.pyint() * -1,
            PositiveFloat: faker.pyint,
            NonPositiveFloat: lambda: uniform(-100, 0),
            NonNegativeInt: faker.pyint,
            StrictInt: faker.pyint,
            StrictBool: faker.pybool,
            StrictBytes: create_random_bytes,
            StrictFloat: faker.pyfloat,
            StrictStr: faker.pystr,
            DirectoryPath: lambda: create_path().parent,
            EmailStr: faker.free_email,
            NameEmail: faker.free_email,
            PyObject: lambda: "decimal.Decimal",
            Color: faker.hex_color,
            Json: faker.json,
            PaymentCardNumber: faker.credit_card_number,
            AnyUrl: faker.url,
            AnyHttpUrl: faker.url,
            HttpUrl: faker.url,
            PostgresDsn: lambda: "postgresql://user:secret@localhost",
            RedisDsn: lambda: "redis://localhost:6379",
            UUID1: uuid1,
            UUID3: lambda: uuid3(NAMESPACE_DNS, faker.pystr()),
            UUID4: uuid4,
            UUID5: lambda: uuid5(NAMESPACE_DNS, faker.pystr()),
            SecretBytes: create_random_bytes,
            SecretStr: faker.pystr,
            IPvAnyAddress: faker.ipv4,
            IPvAnyInterface: faker.ipv4,
            IPvAnyNetwork: lambda: faker.ipv4(network=True),
        }

    @classmethod
    def get_mock_value(cls, field_type: Any) -> Any:
        """
        Returns a mock value corresponding to the types supported by pydantic
        see: https://pydantic-docs.helpmanual.io/usage/types/
        """
        if field_type is not None:
            handler = cls.get_provider_map().get(field_type)
            if handler is not None:
                return handler()
        return None

    @classmethod
    def handle_constrained_field(cls, outer_type: Any) -> Any:
        """Handle the built-in pydantic constrained value field types"""
        try:
            if outer_type.__name__ == "ConstrainedFloatValue":
                return handle_constrained_float(cast(ConstrainedFloat, outer_type))
            if outer_type.__name__ == "ConstrainedIntValue":
                return handle_constrained_int(cast(ConstrainedInt, outer_type))
            if outer_type.__name__ == "ConstrainedDecimalValue":
                return handle_constrained_decimal(cast(ConstrainedDecimal, outer_type))
            if outer_type.__name__ == "ConstrainedStrValue":
                return handle_constrained_string(cast(ConstrainedStr, outer_type))
            if outer_type.__name__ == "ConstrainedBytesValue":
                return handle_constrained_bytes(cast(ConstrainedBytes, outer_type))
            if outer_type.__name__ == "ConstrainedListValue":
                return handle_constrained_list(cast(ConstrainedList, outer_type), cls.get_provider_map())
            if outer_type.__name__ == "ConstrainedSetValue":
                return handle_constrained_set(cast(ConstrainedSet, outer_type), cls.get_provider_map())
            raise ParameterError(f"Unknown constrained field: {outer_type.__name__}")  # pragma: no cover
        except AssertionError as e:
            raise ParameterError from e

    @classmethod
    def handle_enum(cls, outer_type: EnumMeta) -> Any:
        """Method that converts an enum to a list and picks a random element out of it"""
        return choice(list(outer_type))

    @classmethod
    def handle_factory_field(cls, field_name: str) -> Any:
        """Handles a field defined on the factory class itself"""
        value = getattr(cls, field_name)
        if inherits_from(ModelFactory, value):
            return cast(ModelFactory, value).build()
        if callable(value):
            return value()
        return value

    @classmethod
    def create_dynamic_factory(cls, model: BaseModel) -> "ModelFactory":
        """Dynamically generates a factory given a model"""
        return cast(
            ModelFactory,
            type(
                f"{model.__name__}Factory",  # type: ignore
                (ModelFactory,),
                {
                    "__model__": model,
                    "__faker__": cls.get_faker(),
                },
            ),
        )

    @classmethod
    def get_field_value(cls, field_name: str, model_field: ModelField) -> Any:
        """Returns a field value on the sub-class if existing, otherwise returns a mock value"""
        if hasattr(cls, field_name):
            return cls.handle_factory_field(field_name=field_name)
        outer_type = model_field.outer_type_
        if inherits_from(BaseModel, outer_type):
            return cls.create_dynamic_factory(model=outer_type).build()
        if isinstance(outer_type, EnumMeta):
            return cls.handle_enum(outer_type)
        if hasattr(outer_type, "__name__") and "Constrained" in outer_type.__name__:
            return cls.handle_constrained_field(outer_type=outer_type)
        # this is a workaround for the following issue: https://github.com/samuelcolvin/pydantic/issues/3415
        field_type = model_field.type_ if model_field.type_ is not Any else outer_type
        return cls.get_mock_value(field_type=field_type)

    @classmethod
    def build(cls, **kwargs) -> T:
        """builds an instance of the factory's Meta.model"""
        model = cls.get_model_model()
        for field_name, model_field in model.__fields__.items():
            if model_field.alias:
                field_name = model_field.alias
            if field_name not in kwargs:
                kwargs[field_name] = cls.get_field_value(field_name=field_name, model_field=model_field)
        return cls.__model__(**kwargs)

    @classmethod
    def batch(cls, size: int, **kwargs) -> List[T]:
        """builds a batch of size n of the factory's Meta.model"""
        return [cls.build(**kwargs) for _ in range(size)]

    @classmethod
    def create_sync(cls, **kwargs) -> T:
        """Build and persist a single model instance synchronously"""
        sync_persistence_handler = cls.get_sync_persistence()
        instance = cls.build(**kwargs)
        return sync_persistence_handler.save(instance)

    @classmethod
    def create_batch_sync(cls, size: int, **kwargs) -> List[T]:
        """Build and persist a batch of n size model instances synchronously"""
        sync_persistence_handler = cls.get_sync_persistence()
        batch = cls.batch(size, **kwargs)
        return sync_persistence_handler.save_many(batch)

    @classmethod
    async def create_async(cls, **kwargs) -> T:
        """Build and persist a single model instance asynchronously"""
        async_persistence_handler = cls.get_async_persistence()
        instance = cls.build(**kwargs)
        return await async_persistence_handler.save(instance)

    @classmethod
    async def create_batch_async(cls, size: int, **kwargs) -> List[T]:
        """Build and persist a batch of n size model instances asynchronously"""
        async_persistence_handler = cls.get_async_persistence()
        batch = cls.batch(size, **kwargs)
        return await async_persistence_handler.save_many(batch)
