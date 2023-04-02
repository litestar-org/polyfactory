from __future__ import annotations
from abc import ABC, abstractmethod
from collections import Counter, deque
from contextlib import suppress
from datetime import date, datetime, time, timedelta
from decimal import Decimal
from enum import EnumMeta
from functools import partial
from importlib import import_module
from inspect import isclass
from ipaddress import (
    IPv4Address,
    IPv4Interface,
    IPv4Network,
    IPv6Address,
    IPv6Interface,
    IPv6Network,
)
from os.path import realpath
from pathlib import Path
from random import Random
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    ClassVar,
    Generic,
    Mapping,
    Sequence,
    Type,
    TypeVar,
    cast,
)
from uuid import NAMESPACE_DNS, UUID, uuid1, uuid3, uuid5

from faker import Faker
from typing_extensions import get_args

from polyfactory.exceptions import (
    ConfigurationException,
    MissingBuildKwargException,
    ParameterException,
)
from polyfactory.fields import Fixture, Ignore, PostGenerated, Require, Use

from polyfactory.utils.helpers import unwrap_annotation, unwrap_args, unwrap_optional
from polyfactory.utils.predicates import (
    get_type_origin,
    is_literal,
    is_optional_union,
    is_safe_subclass,
)
from polyfactory.value_generators.complex_types import handle_complex_type
from polyfactory.value_generators.primitives import (
    create_random_boolean,
    create_random_bytes,
)

if TYPE_CHECKING:
    from polyfactory.persistence import AsyncPersistenceProtocol, SyncPersistenceProtocol
    from polyfactory.field_meta import FieldMeta
    from typing_extensions import TypeGuard


def _create_pydantic_type_map(cls: "type[BaseFactory]") -> dict[type, Callable[[], Any]]:
    """Creates a mapping of pydantic types to mock data functions.

    :param cls: The base factory class.
    :return: A dict mapping types to callables.
    """
    try:
        import pydantic

        return {
            pydantic.ByteSize: cls.__faker__.pyint,
            pydantic.PositiveInt: cls.__faker__.pyint,
            pydantic.FilePath: lambda: Path(realpath(__file__)),
            pydantic.NegativeFloat: lambda: cls.__random__.uniform(-100, -1),
            pydantic.NegativeInt: lambda: cls.__faker__.pyint() * -1,
            pydantic.PositiveFloat: cls.__faker__.pyint,
            pydantic.NonPositiveFloat: lambda: cls.__random__.uniform(-100, 0),
            pydantic.NonNegativeInt: cls.__faker__.pyint,
            pydantic.StrictInt: cls.__faker__.pyint,
            pydantic.StrictBool: cls.__faker__.pybool,
            pydantic.StrictBytes: partial(create_random_bytes, cls.__random__),
            pydantic.StrictFloat: cls.__faker__.pyfloat,
            pydantic.StrictStr: cls.__faker__.pystr,
            pydantic.DirectoryPath: lambda: Path(realpath(__file__)).parent,
            pydantic.EmailStr: cls.__faker__.free_email,
            pydantic.NameEmail: cls.__faker__.free_email,
            pydantic.PyObject: lambda: "decimal.Decimal",  # type: ignore[dict-item]
            pydantic.color.Color: cls.__faker__.hex_color,  # pyright: ignore
            pydantic.Json: cls.__faker__.json,
            pydantic.PaymentCardNumber: cls.__faker__.credit_card_number,
            pydantic.AnyUrl: cls.__faker__.url,
            pydantic.AnyHttpUrl: cls.__faker__.url,
            pydantic.HttpUrl: cls.__faker__.url,
            pydantic.PostgresDsn: lambda: "postgresql://user:secret@localhost",
            pydantic.RedisDsn: lambda: "redis://localhost:6379",
            pydantic.UUID1: uuid1,
            pydantic.UUID3: lambda: uuid3(NAMESPACE_DNS, cls.__faker__.pystr()),
            pydantic.UUID4: cls.__faker__.uuid4,
            pydantic.UUID5: lambda: uuid5(NAMESPACE_DNS, cls.__faker__.pystr()),
            pydantic.SecretBytes: partial(create_random_bytes, cls.__random__),
            pydantic.SecretStr: cls.__faker__.pystr,
            pydantic.IPvAnyAddress: cls.__faker__.ipv4,
            pydantic.IPvAnyInterface: cls.__faker__.ipv4,
            pydantic.IPvAnyNetwork: lambda: cls.__faker__.ipv4(network=True),
            pydantic.AmqpDsn: lambda: "amqps://",
            pydantic.KafkaDsn: lambda: "kafka://",
            pydantic.PastDate: cls.__faker__.past_date,
            pydantic.FutureDate: cls.__faker__.future_date,
        }
    except ImportError:
        return {}


T = TypeVar("T")


def is_factory(value: Any) -> "TypeGuard[type[BaseFactory]]":
    """Determine if a given value is a subclass of ModelFactory.

    :param value: An arbitrary value.
    :returns: A boolean typeguard.

    """
    return isclass(value) and issubclass(value, BaseFactory)


class BaseFactory(ABC, Generic[T]):
    """Base Factory class - this class holds the main logic of the library"""

    # configuration attributes
    __model__: type[T]
    """
    The model for the factory.
    This attribute is required for non-base factories and an exception will be raised if its not set.
    """
    __allow_none_optionals__: ClassVar[bool] = True
    """
    Flag dictating whether to allow 'None' for optional values.
    If 'True', 'None' will be randomly generated as a value for optional model fields
    """
    __sync_persistence__: type[SyncPersistenceProtocol[T]] | SyncPersistenceProtocol[T] | None = None
    """A sync persistence handler. Can be a class or a class instance."""
    __async_persistence__: type[AsyncPersistenceProtocol[T]] | AsyncPersistenceProtocol[T] | None = None
    """An async persistence handler. Can be a class or a class instance."""
    __set_as_default_factory_for_type__ = False
    """
    Flag dictating whether to set as the default factory for the given type.
    If 'True' the factory will be used instead of dynamically generating a factory for the type.
    """
    __is_base_factory__: bool = False
    """
    Flag dictating whether the factory is a 'base' factory. Base factories are registered globally as handlers for types.
    For example, the 'DataclassFactory', 'TypedDictFactory' and 'ModelFactory' are all base factories.
    """
    __faker__: ClassVar["Faker"] = Faker()
    """
    A faker instance to use. Can be a user provided value.
    """
    __random__: ClassVar["Random"] = Random()
    """
    An instance of 'random.Random' to use.
    """
    __random_seed__: ClassVar[int]
    """
    An integer to seed the factory's Faker and Random instances with.
    This attribute can be used to control random generation.
    """

    # cached attributes
    _fields_metadata: list["FieldMeta"]
    # BaseFactory only attributes
    _factory_type_mapping: ClassVar[dict[Any, type["BaseFactory"]]]
    _base_factories: ClassVar[list[type["BaseFactory"]]]

    def __init_subclass__(cls, *args: Any, **kwargs: Any) -> None:
        super().__init_subclass__(*args, **kwargs)

        if not hasattr(BaseFactory, "_base_factories"):
            BaseFactory._base_factories = []

        if not hasattr(BaseFactory, "_factory_type_mapping"):
            BaseFactory._factory_type_mapping = {}

        if "__is_base_factory__" not in cls.__dict__ or not cls.__is_base_factory__:
            model = getattr(cls, "__model__", None)
            if not model:
                raise ConfigurationException(
                    f"required configuration attribute '__model__' is not set on {cls.__name__}"
                )
            if not cls.is_supported_type(model):
                for factory in BaseFactory._base_factories:
                    if factory.is_supported_type(model):
                        raise ConfigurationException(
                            f"{cls.__name__} does not support {model.__name__}, but this type is support by the {factory.__name__} base factory class. T"
                            f"o resolve this error, subclass the factory from {factory.__name__} instead of {cls.__name__}"
                        )
                    raise ConfigurationException(
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
        """Return a SyncPersistenceHandler if defined for the factory, otherwise raises a ConfigurationException.

        :raises: ConfigurationException
        :returns: SyncPersistenceHandler
        """
        if cls.__sync_persistence__:
            return cls.__sync_persistence__() if callable(cls.__sync_persistence__) else cls.__sync_persistence__
        raise ConfigurationException(
            "A '__sync_persistence__' handler must be defined in the factory to use this method"
        )

    @classmethod
    def _get_async_persistence(cls) -> AsyncPersistenceProtocol[T]:
        """Return a AsyncPersistenceHandler if defined for the factory, otherwise raises a ConfigurationException.

        :raises: ConfigurationException
        :returns: AsyncPersistenceHandler
        """
        if cls.__async_persistence__:
            return cls.__async_persistence__() if callable(cls.__async_persistence__) else cls.__async_persistence__
        raise ConfigurationException(
            "An '__async_persistence__' handler must be defined in the factory to use this method"
        )

    @classmethod
    def _handle_factory_field(cls, field_value: Any, field_build_parameters: Any | None = None) -> Any:
        """Handle a value defined on the factory class itself.

        :param field_value: A value defined as an attribute on the factory class.
        :param field_build_parameters: Any build parameters passed to the factory as kwarg values.

        :returns: An arbitrary value correlating with the given field_meta value.
        """
        if is_factory(field_value):
            if isinstance(field_build_parameters, Mapping):
                return field_value.build(**field_build_parameters)

            if isinstance(field_build_parameters, Sequence):
                return [field_value.build(**parameter) for parameter in field_build_parameters]

            return field_value.build()

        if isinstance(field_value, Use):
            return field_value.to_value()

        if isinstance(field_value, Fixture):
            return field_value.to_value()

        if callable(field_value):
            return field_value()

        return field_value

    @classmethod
    def _get_or_create_factory(
        cls,
        model: type,
    ) -> type["BaseFactory"]:
        """Get a factory from registered factories or generate a factory dynamically.

        :param model: A model type.
        :returns: A Factory sub-class.

        """
        if factory := BaseFactory._factory_type_mapping.get(model):
            return factory

        for factory in BaseFactory._base_factories:
            if factory.is_supported_type(model):
                return factory.create_factory(model)

        raise ParameterException(f"unsupported model type {model.__name__}")  # pragma: no cover

    # Public Methods

    @classmethod
    def is_factory_type(cls, annotation: Any) -> bool:
        """Determine whether a given field is annotated with a type that is supported by a base factory.

        :param annotation: A type annotation.
        :returns: Boolean dictating whether the annotation is a factory type
        """
        return any(factory.is_supported_type(annotation) for factory in BaseFactory._base_factories)

    @classmethod
    def is_batch_factory_type(cls, annotation: Any) -> bool:
        """Determine whether a given field is annotated with a sequence of supported factory types.

        :param annotation: A type annotation.
        :returns: Boolean dictating whether the annotation is a batch factory type
        """
        origin = get_type_origin(annotation) or annotation
        if is_safe_subclass(origin, Sequence) and (args := unwrap_args(annotation)):  # type: ignore
            return len(args) == 1 and BaseFactory.is_factory_type(annotation=args[0])
        return False

    @classmethod
    def extract_field_build_parameters(cls, field_meta: "FieldMeta", build_args: dict[str, Any]) -> Any:
        """Extract from the build kwargs any build parameters passed for a given field meta - if it is a factory type.

        :param field_meta: A field meta instance.
        :param build_args: Any kwargs passed to the factory.
        :returns: Any values
        """
        if build_arg := build_args.get(field_meta.name):
            annotation = unwrap_optional(field_meta.annotation)
            if (
                BaseFactory.is_factory_type(annotation=annotation)
                and isinstance(build_arg, Mapping)
                and not BaseFactory.is_factory_type(annotation=type(build_arg))
            ):
                return build_args.pop(field_meta.name)

            if (
                BaseFactory.is_batch_factory_type(annotation=annotation)
                and isinstance(build_arg, Sequence)
                and not any(BaseFactory.is_factory_type(annotation=type(value)) for value in build_arg)
            ):
                return build_args.pop(field_meta.name)
        return None

    @classmethod
    @abstractmethod
    def is_supported_type(cls, value: Any) -> "TypeGuard[type[T]]":  # pragma: no cover
        """Determine whether the given value is supported by the factory.

        :param value: An arbitrary value.
        :returns: A typeguard
        """
        raise NotImplementedError

    @classmethod
    def seed_random(cls, seed: int) -> None:
        """Seed faker and random with the given integer.

        :param seed: An integer to set as seed.
        :returns: 'None'

        """
        cls.__random__.seed(seed, version=3)
        Faker.seed(seed)

    @classmethod
    def is_ignored_type(cls, value: Any) -> bool:
        """Check whether a given value is an ignored type.

        :param value: An arbitrary value.

        :notes:
            - This method is meant to be overwritten by extension factories and other subclasses

        :returns: A boolean determining whether the value should be ignored.

        """
        return value is None

    @classmethod
    def get_provider_map(cls) -> dict[Any, Callable[[], Any]]:
        """Map types to callables.

        :notes:
            - This method is distinct to allow overriding.


        :returns: a dictionary mapping types to callables.

        """

        def _create_generic_fn() -> Callable:
            """Return a generic lambda"""
            return lambda *args: None

        return {
            Any: lambda: None,
            # primitives
            object: object,
            float: cls.__faker__.pyfloat,
            int: cls.__faker__.pyint,
            bool: cls.__faker__.pybool,
            str: cls.__faker__.pystr,
            bytes: partial(create_random_bytes, cls.__random__),
            # built-in objects
            dict: cls.__faker__.pydict,
            tuple: cls.__faker__.pytuple,
            list: cls.__faker__.pylist,
            set: cls.__faker__.pyset,
            frozenset: lambda: frozenset(cls.__faker__.pylist()),
            deque: lambda: deque(cls.__faker__.pylist()),
            # standard library objects
            Path: lambda: Path(realpath(__file__)),
            Decimal: cls.__faker__.pydecimal,
            UUID: cls.__faker__.uuid4,
            # datetime
            datetime: cls.__faker__.date_time_between,
            date: cls.__faker__.date_this_decade,
            time: cls.__faker__.time,
            timedelta: cls.__faker__.time_delta,
            # ip addresses
            IPv4Address: cls.__faker__.ipv4,
            IPv4Interface: cls.__faker__.ipv4,
            IPv4Network: lambda: cls.__faker__.ipv4(network=True),
            IPv6Address: cls.__faker__.ipv6,
            IPv6Interface: cls.__faker__.ipv6,
            IPv6Network: lambda: cls.__faker__.ipv6(network=True),
            # types
            Callable: _create_generic_fn,
            Counter: lambda: Counter(cls.__faker__.pystr()),
            **_create_pydantic_type_map(cls),
        }

    @classmethod
    def get_mock_value(cls, annotation: type) -> Any:
        """Return a mock value for a given type.

        :param annotation: An arbitrary type.
        :returns: An arbitrary value.

        """

        if handler := cls.get_provider_map().get(annotation):
            return handler()

        if isclass(annotation):
            # if value is a class we can try to naively instantiate it.
            # this will work for classes that do not require any parameters passed to __init__
            with suppress(Exception):
                return annotation()

        raise ParameterException(
            f"Unsupported type: {annotation!r}"
            f"\n\nEither extend the providers map or add a factory function for this type."
        )

    @classmethod
    def create_factory(
        cls,
        model: type,
        bases: tuple[type["BaseFactory"], ...] | None = None,
        **kwargs: Any,
    ) -> type["BaseFactory"]:
        """Generate a factory for the given type dynamically.

        :param model: A type to model.
        :param bases: Base classes to use when generating the new class.
        :param kwargs: Any kwargs.

        :returns: A 'ModelFactory' subclass.

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
    def get_field_value(cls, field_meta: "FieldMeta", field_build_parameters: Any | None = None) -> Any:
        """Return a field value on the subclass if existing, otherwise returns a mock value.

        :param field_meta: FieldMeta instance.
        :param field_build_parameters: Any build parameters passed to the factory as kwarg values.

        :returns: An arbitrary value.

        """
        if cls.is_ignored_type(field_meta.annotation):
            return None

        if field_meta.constant:
            return field_meta.default

        if cls.should_set_none_value(field_meta=field_meta):
            return None

        unwrapped_annotation = unwrap_annotation(field_meta.annotation)

        if is_literal(annotation=unwrapped_annotation) and (literal_args := get_args(unwrapped_annotation)):
            return cls.__random__.choice(literal_args)

        if isinstance(unwrapped_annotation, EnumMeta):
            return cls.__random__.choice(list(unwrapped_annotation))  # pyright: ignore

        if BaseFactory.is_factory_type(annotation=unwrapped_annotation):
            return cls._get_or_create_factory(model=unwrapped_annotation).build(
                **(field_build_parameters if isinstance(field_build_parameters, Mapping) else {})
            )

        if BaseFactory.is_batch_factory_type(annotation=unwrapped_annotation):
            factory = cls._get_or_create_factory(model=field_meta.type_args[0])
            if isinstance(field_build_parameters, Sequence):
                return [factory.build(**field_parameters) for field_parameters in field_build_parameters]
            return factory.batch(size=cls.__random__.randint(1, 10))

        if field_meta.children:
            return handle_complex_type(field_meta=field_meta, factory=cls)

        return cls.get_mock_value(annotation=unwrapped_annotation)

    @classmethod
    def should_set_none_value(cls, field_meta: "FieldMeta") -> bool:
        """Determine whether a given model field_meta should be set to None.

        :param field_meta: Field metadata.

        :notes:
            - This method is distinct to allow overriding.

        :returns: A boolean determining whether 'None' should be set for the given field_meta.

        """
        return (
            cls.__allow_none_optionals__
            and is_optional_union(field_meta.annotation)
            and create_random_boolean(random=cls.__random__)
        )

    @classmethod
    def should_set_field_value(cls, field_meta: "FieldMeta", **kwargs: Any) -> bool:
        """Determine whether to set a value for a given field_name.

        :param field_meta: FieldMeta instance.
        :param kwargs: Any kwargs passed to the factory.

        :notes:
            - This method is distinct to allow overriding.

        :returns: A boolean determining whether a value should be set for the given field_meta.

        """
        return not field_meta.name.startswith("_") and field_meta.name not in kwargs

    @classmethod
    @abstractmethod
    def get_model_fields(cls) -> list["FieldMeta"]:  # pragma: no cover
        """Retrieve a list of fields from the factory's model.


        :returns: A list of field MetaData instances.

        """
        raise NotImplementedError

    @classmethod
    def process_kwargs(cls, **kwargs: Any) -> dict[str, Any]:
        """Process the given kwargs and generate values for the factory's model.

        :param kwargs: Any build kwargs.

        :returns: A dictionary of build results.

        """
        result: dict[str, Any] = {**kwargs}
        generate_post: dict[str, PostGenerated] = {}

        for field_meta in cls.get_model_fields():
            field_build_parameters = cls.extract_field_build_parameters(field_meta=field_meta, build_args=kwargs)
            if cls.should_set_field_value(field_meta, **kwargs):
                if hasattr(cls, field_meta.name) and field_meta.name in cls.__dict__:
                    field_value = getattr(cls, field_meta.name)
                    if isinstance(field_value, Ignore):
                        continue

                    if isinstance(field_value, Require) and field_meta.name not in kwargs:
                        raise MissingBuildKwargException(f"Require kwarg {field_meta.name} is missing")

                    if isinstance(field_value, PostGenerated):
                        generate_post[field_meta.name] = field_value
                        continue

                    result[field_meta.name] = cls._handle_factory_field(
                        field_value=field_value,
                        field_build_parameters=field_build_parameters,
                    )
                    continue

                result[field_meta.name] = cls.get_field_value(field_meta, field_build_parameters=field_build_parameters)

        for field_name, post_generator in generate_post.items():
            result[field_name] = post_generator.to_value(field_name, result)

        return result

    @classmethod
    def build(cls, **kwargs: Any) -> T:
        """Build an instance of the factory's __model__

        :param kwargs: Any kwargs. If field names are set in kwargs, their values will be used.

        :returns: An instance of type T.

        """

        return cast("T", cls.__model__(**cls.process_kwargs(**kwargs)))

    @classmethod
    def batch(cls, size: int, **kwargs: Any) -> list[T]:
        """Build a batch of size n of the factory's Meta.model.

        :param size: Size of the batch.
        :param kwargs: Any kwargs. If field_meta names are set in kwargs, their values will be used.

        :returns: A list of instances of type T.

        """
        return [cls.build(**kwargs) for _ in range(size)]

    @classmethod
    def create_sync(cls, **kwargs: Any) -> T:
        """Build and persists synchronously a single model instance.

        :param kwargs: Any kwargs. If field_meta names are set in kwargs, their values will be used.

        :returns: An instance of type T.

        """
        return cls._get_sync_persistence().save(data=cls.build(**kwargs))

    @classmethod
    def create_batch_sync(cls, size: int, **kwargs: Any) -> list[T]:
        """Build and persists synchronously a batch of n size model instances.

        :param size: Size of the batch.
        :param kwargs: Any kwargs. If field_meta names are set in kwargs, their values will be used.

        :returns: A list of instances of type T.

        """
        return cls._get_sync_persistence().save_many(data=cls.batch(size, **kwargs))

    @classmethod
    async def create_async(cls, **kwargs: Any) -> T:
        """Build and persists asynchronously a single model instance.

        :param kwargs: Any kwargs. If field_meta names are set in kwargs, their values will be used.

        :returns: An instance of type T.
        """
        return await cls._get_async_persistence().save(data=cls.build(**kwargs))

    @classmethod
    async def create_batch_async(cls, size: int, **kwargs: Any) -> list[T]:
        """Build and persists asynchronously a batch of n size model instances.


        :param size: Size of the batch.
        :param kwargs: Any kwargs. If field_meta names are set in kwargs, their values will be used.

        :returns: A list of instances of type T.
        """
        return await cls._get_async_persistence().save_many(data=cls.batch(size, **kwargs))


def _register_builtin_factories() -> None:
    """This function is used to register the base factories, if present.

    :returns: None
    """
    import polyfactory.factories.dataclass_factory
    import polyfactory.factories.typed_dict_factory  # noqa: F401

    for module in [
        "polyfactory.factories.pydantic_factory",
        "polyfactory.factories.beanie_odm_factory",
        "polyfactory.factories.odmantic_odm_factory",
    ]:
        try:
            import_module(module)
        except ImportError:
            continue


_register_builtin_factories()
