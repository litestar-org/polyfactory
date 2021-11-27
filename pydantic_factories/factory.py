import os
from abc import ABC
from collections import deque
from dataclasses import is_dataclass
from datetime import date, datetime, time, timedelta
from decimal import Decimal
from enum import EnumMeta
from inspect import isclass
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
from typing import Any, Callable, Dict, Generic, List, Optional, TypeVar, Union, cast
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

from pydantic_factories.constraints.constrained_collection_handler import (
    handle_constrained_collection,
)
from pydantic_factories.constraints.constrained_decimal_handler import (
    handle_constrained_decimal,
)
from pydantic_factories.constraints.constrained_float_handler import (
    handle_constrained_float,
)
from pydantic_factories.constraints.constrained_integer_handler import (
    handle_constrained_int,
)
from pydantic_factories.constraints.strings import (
    handle_constrained_bytes,
    handle_constrained_string,
)
from pydantic_factories.exceptions import (
    ConfigurationError,
    MissingBuildKwargError,
    ParameterError,
)
from pydantic_factories.fields import Ignore, Require
from pydantic_factories.protocols import (
    AsyncPersistenceProtocol,
    DataclassProtocol,
    SyncPersistenceProtocol,
)
from pydantic_factories.utils import get_model_fields, is_optional, is_pydantic_model
from pydantic_factories.value_generators.complex_types import handle_complex_type
from pydantic_factories.value_generators.primitives import (
    create_random_boolean,
    create_random_bytes,
)

T = TypeVar("T", BaseModel, DataclassProtocol)

default_faker = Faker()


class ModelFactory(ABC, Generic[T]):
    __model__: Type[T]
    __faker__: Optional[Faker]
    __sync_persistence__: Optional[Union[Type[SyncPersistenceProtocol[T]], SyncPersistenceProtocol[T]]]
    __async_persistence__: Optional[Union[Type[AsyncPersistenceProtocol[T]], AsyncPersistenceProtocol[T]]]

    @classmethod
    def is_model_factory(cls, value: Any) -> bool:
        """Method to determine if a given value is a subclass of ModelFactory"""
        return isclass(value) and issubclass(value, ModelFactory)

    @classmethod
    def is_constrained_field(cls, value: Any) -> bool:
        """Method to determine if a given value is a pydantic Constrained Field"""
        return isclass(value) and any(
            issubclass(value, c)
            for c in [
                ConstrainedBytes,
                ConstrainedDecimal,
                ConstrainedFloat,
                ConstrainedInt,
                ConstrainedList,
                ConstrainedSet,
                ConstrainedStr,
            ]
        )

    @classmethod
    def is_ignored_type(cls, value: Any) -> bool:
        """
        Checks whether a given value is an ignored type

        Note: This method is meant to be overwritten by extension factories and other subclasses
        """
        return value is None

    @classmethod
    def _get_model(cls) -> Type[T]:
        """
        Returns the factory's model
        """
        if not hasattr(cls, "__model__") or not cls.__model__:
            raise ConfigurationError("missing model class in factory Meta")
        model = cls.__model__
        if is_pydantic_model(model):
            cast(BaseModel, model).update_forward_refs()
        return model

    @classmethod
    def _get_sync_persistence(cls) -> SyncPersistenceProtocol[T]:
        """
        Returns a sync_persistence interface if present
        """
        try:
            persistence = getattr(cls, "__sync_persistence__")
            return persistence if not isclass(persistence) else persistence()
        except AttributeError as e:
            raise ConfigurationError(
                "A sync_persistence handler must be defined in the factory to use this method"
            ) from e

    @classmethod
    def _get_async_persistence(cls) -> AsyncPersistenceProtocol[T]:
        """
        Returns an async_persistence interface
        """
        try:
            persistence = getattr(cls, "__async_persistence__")
            return persistence if not isclass(persistence) else persistence()
        except AttributeError as e:
            raise ConfigurationError(
                "An async_persistence handler must be defined in the factory to use this method"
            ) from e

    @classmethod
    def _get_faker(cls) -> Faker:
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

        faker = cls._get_faker()

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
        handler = cls.get_provider_map().get(field_type)
        if handler is not None:
            return handler()
        return None  # pragma: no cover

    @classmethod
    def handle_constrained_field(cls, model_field: ModelField) -> Any:
        """Handle the built-in pydantic constrained value field types"""
        outer_type = model_field.outer_type_
        try:
            if issubclass(outer_type, ConstrainedFloat):
                return handle_constrained_float(field=cast(ConstrainedFloat, outer_type))
            if issubclass(outer_type, ConstrainedInt):
                return handle_constrained_int(field=cast(ConstrainedInt, outer_type))
            if issubclass(outer_type, ConstrainedDecimal):
                return handle_constrained_decimal(field=cast(ConstrainedDecimal, outer_type))
            if issubclass(outer_type, ConstrainedStr):
                return handle_constrained_string(field=cast(ConstrainedStr, outer_type))
            if issubclass(outer_type, ConstrainedBytes):
                return handle_constrained_bytes(field=cast(ConstrainedBytes, outer_type))
            if issubclass(outer_type, ConstrainedSet) or issubclass(outer_type, ConstrainedList):
                collection_type = list if issubclass(outer_type, ConstrainedList) else set
                return handle_constrained_collection(
                    collection_type=collection_type, model_field=model_field, model_factory=cls  # type: ignore
                )
            raise ParameterError(f"Unknown constrained field: {outer_type.__name__}")  # pragma: no cover
        except AssertionError as e:  # pragma: no cover
            raise ParameterError from e

    @classmethod
    def handle_enum(cls, outer_type: EnumMeta) -> Any:
        """Method that converts an enum to a list and picks a random element out of it"""
        return choice(list(outer_type))

    @classmethod
    def handle_factory_field(cls, field_name: str) -> Any:
        """Handles a field defined on the factory class itself"""
        from pydantic_factories.fields import Use

        value = getattr(cls, field_name)
        if isinstance(value, Use):
            return value.to_value()
        if cls.is_model_factory(value):
            return cast(ModelFactory, value).build()
        if callable(value):
            return value()
        return value

    @classmethod
    def create_factory(cls, model: Type[BaseModel]) -> "ModelFactory":
        """Dynamically generates a factory given a model"""
        return cast(
            ModelFactory,
            type(
                f"{model.__name__}Factory",
                (ModelFactory,),
                {
                    "__model__": model,
                    "__faker__": cls._get_faker(),
                },
            ),
        )

    @classmethod
    def get_field_value(cls, field_name: str, model_field: ModelField) -> Any:
        """Returns a field value on the sub-class if existing, otherwise returns a mock value"""
        if hasattr(cls, field_name):
            return cls.handle_factory_field(field_name=field_name)
        if model_field.field_info.const:
            return model_field.get_default()
        if is_optional(model_field=model_field) and not create_random_boolean():
            return None
        outer_type = model_field.outer_type_
        if isinstance(outer_type, EnumMeta):
            return cls.handle_enum(outer_type)
        if is_pydantic_model(outer_type) or is_dataclass(outer_type):
            return cls.create_factory(model=outer_type).build()
        if cls.is_constrained_field(outer_type):
            return cls.handle_constrained_field(model_field=model_field)
        if model_field.sub_fields:
            return handle_complex_type(model_field=model_field, model_factory=cls)
        # this is a workaround for the following issue: https://github.com/samuelcolvin/pydantic/issues/3415
        field_type = model_field.type_ if model_field.type_ is not Any else outer_type
        if cls.is_ignored_type(field_type):
            return None
        return cls.get_mock_value(field_type=field_type)

    @classmethod
    def should_set_field_value(cls, field_name: str, **kwargs) -> bool:
        """
        Ascertain whether to set a value for a given field_name

        Separated to its own method to allow black-listing field names in sub-classes
        """
        is_field_ignored = False
        is_field_in_kwargs = field_name in kwargs
        if hasattr(cls, field_name):
            value = getattr(cls, field_name)
            if isinstance(value, Require) and not is_field_in_kwargs:
                raise MissingBuildKwargError(f"Require kwarg {field_name} is missing")
            is_field_ignored = isinstance(value, Ignore)
        return not is_field_ignored and not is_field_in_kwargs

    @classmethod
    def build(cls, **kwargs) -> T:
        """builds an instance of the factory's Meta.model"""
        for field_name, model_field in get_model_fields(cls._get_model()):
            if model_field.alias:
                field_name = model_field.alias
            if cls.should_set_field_value(field_name, **kwargs):
                kwargs[field_name] = cls.get_field_value(field_name=field_name, model_field=model_field)
        return cls.__model__(**kwargs)

    @classmethod
    def batch(cls, size: int, **kwargs) -> List[T]:
        """builds a batch of size n of the factory's Meta.model"""
        return [cls.build(**kwargs) for _ in range(size)]

    @classmethod
    def create_sync(cls, **kwargs) -> T:
        """Build and persist a single model instance synchronously"""
        sync_persistence_handler = cls._get_sync_persistence()
        instance = cls.build(**kwargs)
        return sync_persistence_handler.save(data=instance)

    @classmethod
    def create_batch_sync(cls, size: int, **kwargs) -> List[T]:
        """Build and persist a batch of n size model instances synchronously"""
        sync_persistence_handler = cls._get_sync_persistence()
        batch = cls.batch(size, **kwargs)
        return sync_persistence_handler.save_many(data=batch)

    @classmethod
    async def create_async(cls, **kwargs) -> T:
        """Build and persist a single model instance asynchronously"""
        async_persistence_handler = cls._get_async_persistence()
        instance = cls.build(**kwargs)
        return await async_persistence_handler.save(data=instance)

    @classmethod
    async def create_batch_async(cls, size: int, **kwargs) -> List[T]:
        """Build and persist a batch of n size model instances asynchronously"""
        async_persistence_handler = cls._get_async_persistence()
        batch = cls.batch(size, **kwargs)
        return await async_persistence_handler.save_many(data=batch)
