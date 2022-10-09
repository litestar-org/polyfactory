import os
import random
from abc import ABC
from collections import Counter, deque
from contextlib import suppress
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
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    ClassVar,
    Dict,
    Generic,
    ItemsView,
    List,
    Optional,
    Type,
    TypeVar,
    Union,
    cast,
)
from uuid import NAMESPACE_DNS, UUID, uuid1, uuid3, uuid5

from faker import Faker
from pydantic import (
    UUID1,
    UUID3,
    UUID4,
    UUID5,
    AmqpDsn,
    AnyHttpUrl,
    AnyUrl,
    BaseModel,
    ByteSize,
    ConstrainedBytes,
    ConstrainedDecimal,
    ConstrainedFloat,
    ConstrainedFrozenSet,
    ConstrainedInt,
    ConstrainedList,
    ConstrainedSet,
    ConstrainedStr,
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
from pydantic.fields import SHAPE_MAPPING
from typing_extensions import TypeGuard, get_args

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
from pydantic_factories.utils import (
    create_model_from_dataclass,
    is_literal,
    is_optional,
    is_pydantic_model,
)
from pydantic_factories.value_generators.complex_types import handle_complex_type
from pydantic_factories.value_generators.primitives import (
    create_random_boolean,
    create_random_bytes,
)

if TYPE_CHECKING:
    from pydantic.fields import ModelField

T = TypeVar("T", bound=Union[BaseModel, DataclassProtocol])

default_faker = Faker()


class ModelFactory(ABC, Generic[T]):  # noqa: B024
    __model__: ClassVar[Type[T]]  # type: ignore[misc]
    __faker__: ClassVar[Optional[Faker]]
    __sync_persistence__: ClassVar[  # type: ignore[misc]
        Optional[Union[Type[SyncPersistenceProtocol[T]], SyncPersistenceProtocol[T]]]
    ] = None
    __async_persistence__: ClassVar[  # type: ignore[misc]
        Optional[Union[Type[AsyncPersistenceProtocol[T]], AsyncPersistenceProtocol[T]]]
    ] = None
    __allow_none_optionals__: ClassVar[bool] = True
    __random_seed__: ClassVar[Optional[int]] = None

    # Private Methods

    @classmethod
    def _get_model(cls) -> Type[T]:
        """Returns the factory's model."""
        if not hasattr(cls, "__model__") or not cls.__model__:
            raise ConfigurationError("missing model class in factory Meta")
        model = cls.__model__
        if is_pydantic_model(model):
            with suppress(NameError):
                cast("BaseModel", model).update_forward_refs()
        return model

    @classmethod
    def _get_sync_persistence(cls) -> SyncPersistenceProtocol[T]:
        """Returns a sync_persistence interface if present."""
        persistence = cls.__sync_persistence__
        if persistence:
            return persistence if not callable(persistence) else persistence()  # pylint: disable=not-callable
        raise ConfigurationError("A sync_persistence handler must be defined in the factory to use this method")

    @classmethod
    def _get_async_persistence(cls) -> AsyncPersistenceProtocol[T]:
        """Returns an async_persistence interface."""
        persistence = cls.__async_persistence__
        if persistence:
            return persistence if not callable(persistence) else persistence()  # pylint: disable=not-callable
        raise ConfigurationError("An async_persistence handler must be defined in the factory to use this method")

    @classmethod
    def _is_kwargs_missing_pydantic_fields(cls, pydantic_model: Type[T], pydantic_model_kwargs: Any) -> bool:
        """Determines if the kwargs are missing fields that should be defined
        in the pydantic model.

        Returns False if all fields of the pydantic model are defined in
        the kwargs, and True otherwise.
        """
        if is_pydantic_model(pydantic_model_kwargs.__class__) or pydantic_model_kwargs is None:
            return False
        pydantic_model_fields = cls.get_model_fields(pydantic_model)
        pydantic_model_field_names = {field_name for field_name, _ in pydantic_model_fields}
        kwargs_field_names = set(pydantic_model_kwargs.keys())
        return bool(pydantic_model_field_names - kwargs_field_names)

    @classmethod
    def _is_pydantic_with_partial_fields(cls, field_name: str, model_field: "ModelField", **kwargs: Any) -> bool:
        """Determines if the field is a pydantic model AND if the kwargs are
        missing fields that should be defined in the pydantic model.

        Returns False if model_field isn't a Pydantic model OR if all
        fields of the pydantic model are defined in the kwargs, and True
        otherwise.
        """
        pydantic_model = model_field.type_
        if not is_pydantic_model(pydantic_model) or model_field.shape == SHAPE_MAPPING:
            return False

        list_of_pydantic_models_kwargs = kwargs.get(field_name)
        if not isinstance(list_of_pydantic_models_kwargs, list):
            return cls._is_kwargs_missing_pydantic_fields(pydantic_model, list_of_pydantic_models_kwargs)

        return any(
            cls._is_kwargs_missing_pydantic_fields(pydantic_model, pydantic_model_kwargs)
            for pydantic_model_kwargs in list_of_pydantic_models_kwargs
        )

    @classmethod
    def _should_use_alias_name(cls, model_field: "ModelField", model: Type[T]) -> bool:
        """Determines whether a given model field should be set by an alias."""
        if not model_field.alias:
            return False

        if issubclass(model, BaseModel) and model.__config__.allow_population_by_field_name:
            return False
        return True

    @classmethod
    def _handle_constrained_field(cls, model_field: "ModelField") -> Any:
        """Handle the built-in pydantic constrained value field types."""
        outer_type = model_field.outer_type_
        try:
            if issubclass(outer_type, ConstrainedFloat):
                return handle_constrained_float(field=cast("ConstrainedFloat", outer_type))
            if issubclass(outer_type, ConstrainedInt):
                return handle_constrained_int(field=cast("ConstrainedInt", outer_type))
            if issubclass(outer_type, ConstrainedDecimal):
                return handle_constrained_decimal(field=cast("ConstrainedDecimal", outer_type))
            if issubclass(outer_type, ConstrainedStr):
                return handle_constrained_string(
                    field=cast("ConstrainedStr", outer_type), random_seed=cls.__random_seed__
                )
            if issubclass(outer_type, ConstrainedBytes):
                return handle_constrained_bytes(field=cast("ConstrainedBytes", outer_type))
            if issubclass(outer_type, (ConstrainedSet, ConstrainedList, ConstrainedFrozenSet)):
                collection_type = list if issubclass(outer_type, ConstrainedList) else set
                result = handle_constrained_collection(
                    collection_type=collection_type, model_field=model_field, model_factory=cls  # type: ignore
                )
                if issubclass(outer_type, ConstrainedFrozenSet):  # pragma: no cover
                    return frozenset(*result)
                return result
            raise ParameterError(f"Unknown constrained field: {outer_type.__name__}")  # pragma: no cover
        except AssertionError as e:  # pragma: no cover
            raise ParameterError from e

    @classmethod
    def _handle_enum(cls, outer_type: EnumMeta) -> Any:
        """Method that converts an enum to a list and picks a random element
        out of it."""
        return random.choice(list(outer_type))

    @classmethod
    def _handle_factory_field(cls, field_value: Any) -> Any:
        """Handles a field defined on the factory class itself."""
        from pydantic_factories.fields import Use

        if isinstance(field_value, Use):
            return field_value.to_value()
        if cls.is_model_factory(field_value):
            return cast("ModelFactory", field_value).build()
        if callable(field_value):
            return field_value()
        return field_value

    # Public Methods

    @classmethod
    def seed_random(cls, seed: int) -> None:
        """Seeds Fake and random methods with seed.

        Args:
            seed: See value.

        Returns:
            'None'
        """
        random.seed(seed, version=3)
        Faker.seed(seed)
        cls.__random_seed__ = seed

    @classmethod
    def is_model_factory(cls, value: Any) -> TypeGuard[Type["ModelFactory"]]:
        """Method to determine if a given value is a subclass of ModelFactory.

        Args:
            value: An arbitrary value.

        Returns:
            A boolean typeguard.
        """
        return isclass(value) and issubclass(value, ModelFactory)

    @classmethod
    def is_constrained_field(
        cls, value: Any
    ) -> TypeGuard[
        Union[
            Type[ConstrainedBytes],
            Type[ConstrainedDecimal],
            Type[ConstrainedFloat],
            Type[ConstrainedFrozenSet],
            Type[ConstrainedInt],
            Type[ConstrainedList],
            Type[ConstrainedSet],
            Type[ConstrainedStr],
        ]
    ]:
        """Method to determine if a given value is a pydantic Constrained
        Field.

        Args:
            value: An arbitrary value.

        Returns:
            A boolean typeguard.
        """
        return isclass(value) and any(
            issubclass(value, c)
            for c in (
                ConstrainedBytes,
                ConstrainedDecimal,
                ConstrainedFloat,
                ConstrainedFrozenSet,
                ConstrainedInt,
                ConstrainedList,
                ConstrainedSet,
                ConstrainedStr,
            )
        )

    @classmethod
    def is_ignored_type(cls, value: Any) -> bool:
        """Checks whether a given value is an ignored type.

        Args:
            value: An arbitrary value.

        Notes:
            - This method is meant to be overwritten by extension factories and other subclasses

        Returns:
            A boolean determining whether the value should be ignore or not.
        """
        return value is None

    @classmethod
    def get_faker(cls) -> Faker:
        """Returns the instance of faker used by the factory..

        Returns:
            An instance of 'Faker'
        """
        if hasattr(cls, "__faker__") and cls.__faker__:
            return cls.__faker__
        return default_faker

    @classmethod
    def get_provider_map(cls) -> Dict[Any, Callable]:
        """
        Notes:
            - This method is distinct to allow overriding.

        Returns:
            a dictionary mapping types to callables.
        """

        def create_path() -> Path:
            return Path(os.path.realpath(__file__))

        def create_generic_fn() -> Callable:
            return lambda *args: None

        faker = cls.get_faker()

        return {
            Any: lambda: None,
            # primitives
            object: object,
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
            NegativeFloat: lambda: random.uniform(-100, -1),
            NegativeInt: lambda: faker.pyint() * -1,
            PositiveFloat: faker.pyint,
            NonPositiveFloat: lambda: random.uniform(-100, 0),
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
            UUID4: faker.uuid4,
            UUID5: lambda: uuid5(NAMESPACE_DNS, faker.pystr()),
            SecretBytes: create_random_bytes,
            SecretStr: faker.pystr,
            IPvAnyAddress: faker.ipv4,
            IPvAnyInterface: faker.ipv4,
            IPvAnyNetwork: lambda: faker.ipv4(network=True),
            AmqpDsn: lambda: "amqps://",
            KafkaDsn: lambda: "kafka://",
            PastDate: faker.past_date,
            FutureDate: faker.future_date,
            Counter: lambda: Counter(faker.pystr()),  # pylint: disable=unhashable-member
        }

    @classmethod
    def get_mock_value(cls, field_type: Any) -> Any:
        """Returns a mock value for a given type.

        Args:
            field_type: An arbitrary type.

        Returns:
            An arbitrary value.
        """
        handler = cls.get_provider_map().get(field_type)
        if handler is not None:
            return handler()
        if isclass(field_type):
            # if value is a class we can try to naively instantiate it.
            # this will work for classes that do not require any parameters passed to __init__
            with suppress(Exception):
                return field_type()
        raise ParameterError(
            f"Unsupported type: {field_type!r}"
            f"\n\nEither extend the providers map or add a factory function for this model field"
        )

    @classmethod
    def create_factory(
        cls,
        model: Type[BaseModel],
        base: Optional[Type["ModelFactory"]] = None,
        **kwargs: Any,
    ) -> "ModelFactory":
        """Dynamically generates a 'ModelFactory' for a given pydantic model
        subclass.

        Args:
            model: A pydantic model subclass.
            base: A base factory to use.
            **kwargs: Any kwargs.

        Returns:
            A 'ModelFactory' subclass.
        """

        kwargs.setdefault("__faker__", cls.get_faker())
        kwargs.setdefault("__sync_persistence__", cls.__sync_persistence__)
        kwargs.setdefault("__async_persistence__", cls.__async_persistence__)
        kwargs.setdefault("__allow_none_optionals__", cls.__allow_none_optionals__)
        kwargs.setdefault("__random__seed__", cls.__random_seed__)
        return cast(
            "ModelFactory",
            type(
                f"{model.__name__}Factory",
                (base or cls,),
                {"__model__": model, **kwargs},
            ),
        )

    @classmethod
    def get_field_value(
        cls, model_field: "ModelField", field_parameters: Optional[Union[Dict[Any, Any], List[Any]]] = None
    ) -> Any:
        """Returns a field value on the subclass if existing, otherwise returns
        a mock value.

        Args:
            model_field: A pydantic 'ModelField'.
            field_parameters: Any parameters related to the model field.

        Returns:
            An arbitrary value.
        """
        if model_field.field_info.const:
            return model_field.get_default()
        if cls.should_set_none_value(model_field=model_field):
            return None
        outer_type = model_field.outer_type_
        if isinstance(outer_type, EnumMeta):
            return cls._handle_enum(outer_type)
        if is_pydantic_model(outer_type) or is_dataclass(outer_type):
            build_kwargs: dict = field_parameters or {}  # type: ignore
            return cls.create_factory(model=outer_type).build(**build_kwargs)
        if isinstance(field_parameters, list) and is_pydantic_model(model_field.type_):
            return [
                cls.create_factory(model=model_field.type_).build(**build_kwargs) for build_kwargs in field_parameters
            ]
        if cls.is_constrained_field(outer_type):
            return cls._handle_constrained_field(model_field=model_field)
        if model_field.sub_fields:
            return handle_complex_type(model_field=model_field, model_factory=cls, field_parameters=field_parameters)
        if is_literal(model_field):
            literal_args = get_args(outer_type)
            return random.choice(literal_args)
        # this is a workaround for the following issue: https://github.com/samuelcolvin/pydantic/issues/3415
        field_type = model_field.type_ if model_field.type_ is not Any else outer_type
        if cls.is_ignored_type(field_type):
            return None
        return cls.get_mock_value(field_type=field_type)

    @classmethod
    def should_set_none_value(cls, model_field: "ModelField") -> bool:
        """Determines whether a given model field should be set to None.

        Args:
            model_field: A pydantic 'ModelField'.

        Notes:
            - This method is distinct to allow overriding.

        Returns:
            A boolean determining whether 'None' should be set for the given field.
        """
        if cls.__allow_none_optionals__:
            return is_optional(model_field=model_field) and not create_random_boolean()
        return False

    @classmethod
    def should_set_field_value(cls, field_name: str, model_field: "ModelField", **kwargs: Dict[str, Any]) -> bool:
        """Determine whether to set a value for a given field_name.

        Args:
            field_name:
            model_field:
            **kwargs:

        Notes:
            - This method is distinct to allow overriding.

        Returns:
            A boolean determining whether a value should be set for the given field.
        """
        is_field_ignored = False
        is_field_in_kwargs = field_name in kwargs
        is_partial_pydantic_model = cls._is_pydantic_with_partial_fields(field_name, model_field, **kwargs)
        if hasattr(cls, field_name):
            value = getattr(cls, field_name)
            if isinstance(value, Require) and not is_field_in_kwargs:
                raise MissingBuildKwargError(f"Require kwarg {field_name} is missing")
            is_field_ignored = isinstance(value, Ignore)
        return not is_field_ignored and (not is_field_in_kwargs or is_partial_pydantic_model)

    @classmethod
    def get_model_fields(cls, model: Type[T]) -> ItemsView[str, "ModelField"]:
        """A function to retrieve the fields of a given model.

        If the model passed is a dataclass, it's converted to a pydantic
        model first.

        Args:
            model: An arbitrary type T.

        Notes:
            - This method is distinct to allow overriding.

        Returns:
            An 'ItemsView' composed of field names and pydantic 'ModelField' instances.
        """
        if not is_pydantic_model(model):
            model = create_model_from_dataclass(dataclass=model)  # type: ignore
        return model.__fields__.items()  # type: ignore

    @classmethod
    def build(cls, factory_use_construct: bool = False, **kwargs: Any) -> T:
        """builds an instance of the factory's __model__

        Args:
            factory_use_construct: A boolea that determines whether validations will be made when instantiating the
                model. this is supported only for pydantic models.
            **kwargs: Any kwargs. If field names are set in kwargs, their values will be used.

        Returns:
            An instance of type T.
        """
        from pydantic_factories.fields import PostGenerated

        generate_post: Dict[str, PostGenerated] = {}

        model = cls._get_model()
        for field_name, model_field in cls.get_model_fields(model):
            if cls._should_use_alias_name(model_field, model):
                field_name = model_field.alias
            if cls.should_set_field_value(field_name, model_field, **kwargs):
                if hasattr(cls, field_name):
                    value = getattr(cls, field_name)
                    if isinstance(value, PostGenerated):
                        generate_post[field_name] = value
                    else:
                        kwargs[field_name] = cls._handle_factory_field(field_value=value)
                else:
                    kwargs[field_name] = cls.get_field_value(model_field, field_parameters=kwargs.get(field_name, {}))
        for field_name, post_generator in generate_post.items():
            kwargs[field_name] = post_generator.to_value(field_name, kwargs)
        if factory_use_construct:
            if is_pydantic_model(cls.__model__):
                return cls.__model__.construct(**kwargs)  # type: ignore
            raise ConfigurationError("factory_use_construct requires a pydantic model as the factory's __model__")
        return cast("T", cls.__model__(**kwargs))

    @classmethod
    def batch(cls, size: int, **kwargs: Any) -> List[T]:
        """Builds a batch of size n of the factory's Meta.model.

        Args:
            size: Size of the batch.
            **kwargs: Any kwargs. If field names are set in kwargs, their values will be used.

        Returns:
            A list of instances of type T.
        """
        return [cls.build(**kwargs) for _ in range(size)]

    @classmethod
    def create_sync(cls, **kwargs: Any) -> T:
        """Builds and persists synchronously a single model instance.

        Args:
            **kwargs: Any kwargs. If field names are set in kwargs, their values will be used.

        Returns:
            An instance of type T.
        """
        sync_persistence_handler = cls._get_sync_persistence()
        instance = cls.build(**kwargs)
        return sync_persistence_handler.save(data=instance)

    @classmethod
    def create_batch_sync(cls, size: int, **kwargs: Any) -> List[T]:
        """Builds and persists synchronously a batch of n size model instances.

        Args:
            size: Size of the batch.
            **kwargs: Any kwargs. If field names are set in kwargs, their values will be used.

        Returns:
            A list of instances of type T.
        """
        sync_persistence_handler = cls._get_sync_persistence()
        batch = cls.batch(size, **kwargs)
        return sync_persistence_handler.save_many(data=batch)

    @classmethod
    async def create_async(cls, **kwargs: Any) -> T:
        """Builds and persists asynchronously a single model instance.

        Args:
            **kwargs: Any kwargs. If field names are set in kwargs, their values will be used.

        Returns:
            An instance of type T.
        """
        async_persistence_handler = cls._get_async_persistence()
        instance = cls.build(**kwargs)
        return await async_persistence_handler.save(data=instance)

    @classmethod
    async def create_batch_async(cls, size: int, **kwargs: Any) -> List[T]:
        """Builds and persists asynchronously a batch of n size model
        instances.

        Args:
            size: Size of the batch.
            **kwargs: Any kwargs. If field names are set in kwargs, their values will be used.

        Returns:
            A list of instances of type T.
        """
        async_persistence_handler = cls._get_async_persistence()
        batch = cls.batch(size, **kwargs)
        return await async_persistence_handler.save_many(data=batch)
