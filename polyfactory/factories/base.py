from abc import ABC, abstractmethod
from collections import Counter, deque
from contextlib import suppress
from dataclasses import MISSING, fields, is_dataclass
from datetime import date, datetime, time, timedelta
from decimal import Decimal
from enum import EnumMeta
from functools import partial
from inspect import isclass
from ipaddress import (
    IPv4Address,
    IPv4Interface,
    IPv4Network,
    IPv6Address,
    IPv6Interface,
    IPv6Network,
)
from math import nan
from os.path import realpath
from pathlib import Path
from random import Random, choice, uniform
from typing import _TypedDictMeta  # type: ignore
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    ClassVar,
    Dict,
    Generic,
    List,
    Optional,
    Tuple,
    Type,
    TypeVar,
    Union,
    cast,
)
from uuid import NAMESPACE_DNS, UUID, uuid1, uuid3, uuid5

from faker import Faker
from typing_extensions import get_args, is_typeddict

from polyfactory.exceptions import (
    ConfigurationError,
    MissingBuildKwargError,
    ParameterError,
)
from polyfactory.field_meta import FieldMeta, Null
from polyfactory.fields import Fixture, Ignore, PostGenerated, Require, Use
from polyfactory.protocols import AsyncPersistenceProtocol, SyncPersistenceProtocol
from polyfactory.utils.helpers import unwrap_new_type, unwrap_optional, unwrap_union
from polyfactory.utils.predicates import is_literal, is_optional_union
from polyfactory.value_generators.complex_types import handle_complex_type
from polyfactory.value_generators.primitives import (
    create_random_boolean,
    create_random_bytes,
)

if TYPE_CHECKING:
    from typing_extensions import TypeGuard

try:
    from pydantic import (
        UUID1,
        UUID3,
        UUID4,
        UUID5,
        AmqpDsn,
        AnyHttpUrl,
        AnyUrl,
        ByteSize,
        DirectoryPath,
        EmailStr,
        FilePath,
        FutureDate,
        HttpUrl,
        IPvAnyAddress,
        IPvAnyInterface,
        IPvAnyNetwork,
        Json,
        KafkaDsn,
        NameEmail,
        NegativeFloat,
        NegativeInt,
        NonNegativeInt,
        NonPositiveFloat,
        PastDate,
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
except ImportError:
    # we use the fact that 'nan != nan' to ensure that these types are never matched
    Color = nan  # type: ignore[misc, assignment]
    UUID1 = nan  # type: ignore[misc, assignment]
    UUID3 = nan  # type: ignore[misc, assignment]
    UUID4 = nan  # type: ignore[misc, assignment]
    UUID5 = nan  # type: ignore[misc, assignment]
    AmqpDsn = nan  # type: ignore[misc]
    AnyHttpUrl = nan  # type: ignore[misc]
    AnyUrl = nan  # type: ignore[misc]
    ByteSize = nan  # type: ignore[misc, assignment]
    DirectoryPath = nan  # type: ignore[misc, assignment]
    EmailStr = nan  # type: ignore[misc, assignment]
    FilePath = nan  # type: ignore[misc, assignment]
    FutureDate = nan  # type: ignore[misc, assignment]
    HttpUrl = nan  # type: ignore[misc]
    IPvAnyAddress = nan  # type: ignore[misc, assignment]
    IPvAnyInterface = nan  # type: ignore[misc, assignment]
    IPvAnyNetwork = nan  # type: ignore[misc, assignment]
    Json = nan  # type: ignore[misc]
    KafkaDsn = nan  # type: ignore[misc]
    NameEmail = nan  # type: ignore[misc, assignment]
    NegativeFloat = nan  # type: ignore[misc, assignment]
    NegativeInt = nan  # type: ignore[misc, assignment]
    NonNegativeInt = nan  # type: ignore[misc, assignment]
    NonPositiveFloat = nan  # type: ignore[misc, assignment]
    PastDate = nan  # type: ignore[misc, assignment]
    PaymentCardNumber = nan  # type: ignore[misc, assignment]
    PositiveFloat = nan  # type: ignore[misc, assignment]
    PositiveInt = nan  # type: ignore[misc, assignment]
    PostgresDsn = nan  # type: ignore[misc]
    PyObject = nan  # type: ignore[misc]
    RedisDsn = nan  # type: ignore[misc]
    SecretBytes = nan  # type: ignore[misc, assignment]
    SecretStr = nan  # type: ignore[misc, assignment]
    StrictBool = nan  # type: ignore[misc, assignment]
    StrictBytes = nan  # type: ignore[misc, assignment]
    StrictFloat = nan  # type: ignore[misc, assignment]
    StrictInt = nan  # type: ignore[misc, assignment]
    StrictStr = nan  # type: ignore[misc, assignment]


T = TypeVar("T")


def is_factory(value: Any) -> "TypeGuard[Type[BaseFactory]]":
    """Determine if a given value is a subclass of ModelFactory.

    Args:
        value: An arbitrary value.

    Returns:
        A boolean typeguard.
    """
    return isclass(value) and issubclass(value, BaseFactory)


class BaseFactory(ABC, Generic[T]):
    # configuration attributes
    __allow_none_optionals__: ClassVar[bool] = True
    __async_persistence__: Optional[Union[Type[AsyncPersistenceProtocol[T]], AsyncPersistenceProtocol[T]]] = None
    __set_as_default_factory_for_type__ = False
    __is_base_factory__: bool = False
    __faker__: ClassVar["Faker"] = Faker()
    __random__: ClassVar["Random"] = Random()
    __model__: Type[T]
    __random_seed__: ClassVar[int]
    __sync_persistence__: Optional[Union[Type[SyncPersistenceProtocol[T]], SyncPersistenceProtocol[T]]] = None

    # cached attributes
    _fields_metadata: List["FieldMeta"]
    # BaseFactory only attributes
    _factory_type_mapping: ClassVar[Dict[Any, Type["BaseFactory"]]]
    _base_factories: ClassVar[List[Type["BaseFactory"]]]

    def __init_subclass__(cls, *args: Any, **kwargs: Any) -> None:
        super().__init_subclass__(*args, **kwargs)

        if not hasattr(BaseFactory, "_base_factories"):
            BaseFactory._base_factories = []

        if not hasattr(BaseFactory, "_factory_type_mapping"):
            BaseFactory._factory_type_mapping = {}

        if "__is_base_factory__" not in cls.__dict__ or not cls.__is_base_factory__:
            model = getattr(cls, "__model__", None)
            if not model:
                raise ConfigurationError(f"required configuration attribute '__model__' is not set on {cls.__name__}")
            if not cls.is_supported_type(model):
                for factory in BaseFactory._base_factories:
                    if factory.is_supported_type(model):
                        raise ConfigurationError(
                            f"{cls.__name__} does not support {model.__name__}, but this type is support by the {factory.__name__} base factory class. T"
                            f"o resolve this error, subclass the factory from {factory.__name__} instead of {cls.__name__}"
                        )
                    raise ConfigurationError(
                        "Model type {model.__name__} is not supported. "
                        "To support it, register an appropriate base factory and subclass it for your factory."
                    )

        if random_seed := getattr(cls, "__random_seed__", None) is not None:
            cls.seed_random(random_seed)

        if cls.__is_base_factory__:
            BaseFactory._base_factories.append(cls)

        if cls.__set_as_default_factory_for_type__:
            BaseFactory._factory_type_mapping[cls.__model__] = cls

    @classmethod
    def _get_sync_persistence(cls) -> SyncPersistenceProtocol[T]:
        """Returns a sync_persistence interface if present."""
        if cls.__sync_persistence__:
            return cls.__sync_persistence__() if callable(cls.__sync_persistence__) else cls.__sync_persistence__
        raise ConfigurationError("A sync_persistence handler must be defined in the factory to use this method")

    @classmethod
    def _get_async_persistence(cls) -> AsyncPersistenceProtocol[T]:
        """Returns an async_persistence interface."""
        if cls.__async_persistence__:
            return cls.__async_persistence__() if callable(cls.__async_persistence__) else cls.__async_persistence__
        raise ConfigurationError("An async_persistence handler must be defined in the factory to use this method")

    @classmethod
    def _handle_enum(cls, annotation: EnumMeta) -> Any:
        """Method that converts an enum to a list and picks a random element out of it.

        Args:
            annotation: An Enum class.

        Returns:
            A random member value.
        """
        return choice(list(annotation))  # pyright: ignore

    @classmethod
    def _handle_factory_field(cls, field_value: Any) -> Any:
        """Handles a field_meta defined on the factory class itself.

        Args:
            field_value: A value defined as an attribute on the factory class.

        Returns:
            An arbitrary value correlating with the given field_meta value.
        """

        if isinstance(field_value, (Use, Fixture)):
            return field_value.to_value()

        if is_factory(field_value):
            return field_value.build()

        if callable(field_value):
            return field_value()

        return field_value

    @classmethod
    def _get_or_create_factory(
        cls,
        model: Type,
    ) -> Type["BaseFactory"]:
        """Get a factory from registered factories or generate a factory dynamically.

        Args:
            model: A type.
        Returns:
            A Factory subclass.
        """
        if factory := BaseFactory._factory_type_mapping.get(model):
            return factory

        for factory in BaseFactory._base_factories:
            if factory.is_supported_type(model):
                return factory.create_factory(model)

        raise ParameterError(f"unsupported model type {model.__name__}")

    # Public Methods

    @classmethod
    @abstractmethod
    def is_supported_type(cls, value: Any) -> "TypeGuard[Type[T]]":
        """

        :param value:
        :return:
        """
        raise NotImplementedError

    @classmethod
    def seed_random(cls, seed: int) -> None:
        """Seeds Fake and random methods with seed.

        Args:
            seed: See value.

        Returns:
            'None'
        """
        cls.__random__.seed(seed, version=3)
        Faker.seed(seed)

    @classmethod
    def is_ignored_type(cls, value: Any) -> bool:
        """Checks whether a given value is an ignored type.

        Args:
            value: An arbitrary value.

        Notes:
            - This method is meant to be overwritten by extension factories and other subclasses

        Returns:
            A boolean determining whether the value should be ignored.
        """
        return value is None

    @classmethod
    def get_provider_map(cls) -> Dict[Any, Callable[[], Any]]:
        """
        Notes:
            - This method is distinct to allow overriding.

        Returns:
            a dictionary mapping types to callables.
        """

        def create_path() -> Path:
            return Path(realpath(__file__))

        def create_generic_fn() -> Callable:
            return lambda *args: None

        faker = cls.__faker__

        return {
            Any: lambda: None,
            # primitives
            object: object,
            float: faker.pyfloat,
            int: faker.pyint,
            bool: faker.pybool,
            str: faker.pystr,
            bytes: partial(create_random_bytes, cls.__random__),
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
            UUID: faker.uuid4,
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
            StrictBytes: partial(create_random_bytes, cls.__random__),
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
            UUID4: faker.uuid4,
            UUID5: lambda: uuid5(NAMESPACE_DNS, faker.pystr()),
            SecretBytes: partial(create_random_bytes, cls.__random__),
            SecretStr: faker.pystr,
            IPvAnyAddress: faker.ipv4,
            IPvAnyInterface: faker.ipv4,
            IPvAnyNetwork: lambda: faker.ipv4(network=True),
            AmqpDsn: lambda: "amqps://",
            KafkaDsn: lambda: "kafka://",
            PastDate: faker.past_date,
            FutureDate: faker.future_date,
            Counter: lambda: Counter(faker.pystr()),
        }

    @classmethod
    def get_mock_value(cls, annotation: Type) -> Any:
        """Returns a mock value for a given type.

        Args:
            annotation: An arbitrary type.

        Returns:
            An arbitrary value.
        """

        if handler := cls.get_provider_map().get(annotation):
            return handler()

        if isclass(annotation):
            # if value is a class we can try to naively instantiate it.
            # this will work for classes that do not require any parameters passed to __init__
            with suppress(Exception):
                return annotation()

        raise ParameterError(
            f"Unsupported type: {annotation!r}"
            f"\n\nEither extend the providers map or add a factory function for this type."
        )

    @classmethod
    def create_factory(
        cls,
        model: Type,
        bases: Optional[Tuple[Type["BaseFactory"], ...]] = None,
        **kwargs: Any,
    ) -> Type["BaseFactory"]:
        """Dynamically generates a factory for a given type.

        Args:
            model: A type to model.
            bases: Base classes to use when generating the new class.
            **kwargs: Any kwargs.

        Returns:
            A 'ModelFactory' subclass.
        """

        for key in (attr for attr in dir(cls) if attr.startswith("__") and attr != "__model__"):
            kwargs.setdefault(key, getattr(cls, key, None))

        return cast(
            "Type[BaseFactory]",
            type(
                f"{model.__name__}Factory",
                (*(bases or ()), cls),
                {"__model__": model, **kwargs},
            ),
        )

    @classmethod
    def get_field_value(cls, field_meta: "FieldMeta") -> Any:
        """Returns a field value on the subclass if existing, otherwise returns a mock value.

        Args:
            field_meta: FieldMeta instance.

        Returns:
            An arbitrary value.
        """
        if field_meta.constant:
            return field_meta.default

        if cls.should_set_none_value(field_meta=field_meta):
            return None

        field_type = unwrap_new_type(unwrap_optional(field_meta.annotation))
        if isinstance(field_type, EnumMeta):
            return cls._handle_enum(field_type)

        if any(factory.is_supported_type(field_meta.annotation) for factory in BaseFactory._base_factories):
            return cls._get_or_create_factory(model=field_meta.annotation).build(
                **(field_meta.extra if isinstance(field_meta.extra, dict) else {})
            )

        if field_meta.children:
            return handle_complex_type(field_meta=field_meta, factory=cls)

        if is_literal(field_meta.annotation) and (literal_args := get_args(field_meta.annotation)):
            return choice(literal_args)

        if cls.is_ignored_type(field_meta.annotation):
            return None

        return cls.get_mock_value(annotation=unwrap_union(field_type))

    @classmethod
    def should_set_none_value(cls, field_meta: "FieldMeta") -> bool:
        """Determines whether a given model field_meta should be set to None.

        Args:
            field_meta: Field metadata.

        Notes:
            - This method is distinct to allow overriding.

        Returns:
            A boolean determining whether 'None' should be set for the given field_meta.
        """
        return (
            cls.__allow_none_optionals__
            and is_optional_union(field_meta.annotation)
            and create_random_boolean(random=cls.__random__)
        )

    @classmethod
    def should_set_field_value(cls, field_meta: "FieldMeta", **kwargs: Any) -> bool:
        """Determine whether to set a value for a given field_name.

        Args:
            field_meta: FieldMeta instance.
            **kwargs: Any kwargs passed to the factory.

        Notes:
            - This method is distinct to allow overriding.

        Returns:
            A boolean determining whether a value should be set for the given field_meta.
        """
        return not field_meta.name.startswith("_") and field_meta.name not in kwargs

    @classmethod
    @abstractmethod
    def get_model_fields(cls) -> List["FieldMeta"]:
        """
        Retrieve a list of fields from the factory's model.

        Returns:
            A list of field MetaData instances.
        """
        raise NotImplementedError

    @classmethod
    def process_kwargs(cls, **kwargs: Any) -> Dict[str, Any]:
        """

        :param kwargs:
        :return:
        """
        result: Dict[str, Any] = {**kwargs}
        generate_post: Dict[str, PostGenerated] = {}

        for field_meta in cls.get_model_fields():
            if cls.should_set_field_value(field_meta, **kwargs):
                if hasattr(cls, field_meta.name) and field_meta.name in cls.__dict__:
                    field_value = getattr(cls, field_meta.name)
                    if isinstance(field_value, Ignore):
                        continue

                    if isinstance(field_value, Require) and field_meta.name not in kwargs:
                        raise MissingBuildKwargError(f"Require kwarg {field_meta.name} is missing")

                    if isinstance(field_value, PostGenerated):
                        generate_post[field_meta.name] = field_value
                        continue

                    result[field_meta.name] = cls._handle_factory_field(field_value=field_value)
                    continue

                result[field_meta.name] = cls.get_field_value(field_meta)

        for field_name, post_generator in generate_post.items():
            result[field_name] = post_generator.to_value(field_name, result)

        return result

    @classmethod
    def build(cls, **kwargs: Any) -> T:
        """Build an instance of the factory's __model__

        Args:
            **kwargs: Any kwargs. If field_meta names are set in kwargs, their values will be used.

        Returns:
            An instance of type T.
        """

        return cast("T", cls.__model__(**cls.process_kwargs(**kwargs)))

    @classmethod
    def batch(cls, size: int, **kwargs: Any) -> List[T]:
        """Builds a batch of size n of the factory's Meta.model.

        Args:
            size: Size of the batch.
            **kwargs: Any kwargs. If field_meta names are set in kwargs, their values will be used.

        Returns:
            A list of instances of type T.
        """
        return [cls.build(**kwargs) for _ in range(size)]

    @classmethod
    def create_sync(cls, **kwargs: Any) -> T:
        """Builds and persists synchronously a single model instance.

        Args:
            **kwargs: Any kwargs. If field_meta names are set in kwargs, their values will be used.

        Returns:
            An instance of type T.
        """
        return cls._get_sync_persistence().save(data=cls.build(**kwargs))

    @classmethod
    def create_batch_sync(cls, size: int, **kwargs: Any) -> List[T]:
        """Builds and persists synchronously a batch of n size model instances.

        Args:
            size: Size of the batch.
            **kwargs: Any kwargs. If field_meta names are set in kwargs, their values will be used.

        Returns:
            A list of instances of type T.
        """
        return cls._get_sync_persistence().save_many(data=cls.batch(size, **kwargs))

    @classmethod
    async def create_async(cls, **kwargs: Any) -> T:
        """Builds and persists asynchronously a single model instance.

        Args:
            **kwargs: Any kwargs. If field_meta names are set in kwargs, their values will be used.

        Returns:
            An instance of type T.
        """
        return await cls._get_async_persistence().save(data=cls.build(**kwargs))

    @classmethod
    async def create_batch_async(cls, size: int, **kwargs: Any) -> List[T]:
        """Builds and persists asynchronously a batch of n size model instances.

        Args:
            size: Size of the batch.
            **kwargs: Any kwargs. If field_meta names are set in kwargs, their values will be used.

        Returns:
            A list of instances of type T.
        """
        return await cls._get_async_persistence().save_many(data=cls.batch(size, **kwargs))


class DataclassFactory(Generic[T], BaseFactory[T]):
    __is_base_factory__ = True

    @classmethod
    def is_supported_type(cls, value: Any) -> "TypeGuard[Type[T]]":
        try:
            return isclass(value) and is_dataclass(value)
        except (TypeError, AttributeError):
            return False

    @classmethod
    def get_model_fields(cls) -> List["FieldMeta"]:
        fields_meta: List["FieldMeta"] = []

        for field in fields(cls.__model__):
            if field.default_factory and field.default_factory is not MISSING:
                default_value = field.default_factory()
            elif field.default is not MISSING:
                default_value = field.default
            else:
                default_value = Null

            fields_meta.append(FieldMeta.from_type(annotation=field.type, name=field.name, default=default_value))

        return fields_meta


TypedDictT = TypeVar("TypedDictT", bound=_TypedDictMeta)


class TypedDictFactory(Generic[TypedDictT], BaseFactory[TypedDictT]):
    __is_base_factory__ = True

    @classmethod
    def is_supported_type(cls, value: Any) -> "TypeGuard[Type[TypedDictT]]":
        try:
            return is_typeddict(value)
        except (TypeError, AttributeError):
            return False

    @classmethod
    def get_model_fields(cls) -> List["FieldMeta"]:
        fields_meta: List["FieldMeta"] = []

        for field_name, annotation in cls.__model__.__annotations__.items():
            fields_meta.append(
                FieldMeta.from_type(
                    annotation=annotation,
                    name=field_name,
                    default=getattr(cls.__model__, field_name, Null),
                )
            )
        return fields_meta
