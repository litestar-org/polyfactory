import datetime as dt
from decimal import Decimal
from inspect import isclass
from typing import Any, Callable, Dict, FrozenSet, Generic, Iterable, List, Set, Tuple, Type, TypeVar, cast
from uuid import UUID

from typing_extensions import TypeGuard

from polyfactory.exceptions import MissingDependencyException, ParameterException
from polyfactory.factories.base import BaseFactory
from polyfactory.field_meta import Constraints, FieldMeta
from polyfactory.value_generators.constrained_numbers import handle_constrained_int
from polyfactory.value_generators.primitives import create_random_bytes

try:
    import msgspec
    from msgspec import Struct, inspect
    from msgspec.inspect import Field
    from msgspec.inspect import Type as MsgspecType
except ImportError as e:
    raise MissingDependencyException("msgspec is not installed") from e

T = TypeVar("T", bound=Struct)

_NoneType = None.__class__


class MsgspecFactory(Generic[T], BaseFactory[T]):
    """Base factory for msgspec Structs."""

    __is_base_factory__ = True

    _MSGSPEC_TYPE_TO_ANNOTATION_MAP: Dict[Type[MsgspecType], Type] = {
        inspect.AnyType: _NoneType,
        inspect.NoneType: _NoneType,
        inspect.BoolType: bool,
        inspect.IntType: int,
        inspect.FloatType: float,
        inspect.StrType: str,
        inspect.ByteArrayType: bytearray,
        inspect.BytesType: bytes,
        inspect.DateTimeType: dt.datetime,
        inspect.TimeType: dt.time,
        inspect.DateType: dt.date,
        inspect.UUIDType: UUID,
        inspect.DecimalType: Decimal,
        inspect.ExtType: msgspec.msgpack.Ext,
        inspect.RawType: bytes,
    }

    @classmethod
    def get_constraints(cls, field_type: inspect.Type, names: Iterable[str]) -> Constraints:
        """Get the constraints on a field type.

        :param field_type: A msgspec Type instance.
        :param names: The constraint names.

        :returns: The constraints on the given field type.

        """
        constraints = {}
        for name in names:
            constraint = getattr(field_type, name)
            if constraint is not None:
                constraints[name] = constraint

        return cast(Constraints, constraints)

    @classmethod
    def get_collection_type_annotation(cls, msgspec_collection_type: inspect.CollectionType) -> Type:
        """Return the annotation for a msgspec collection type.

        :param msgspec_collection_type: A msgspec CollectionType instance.

        :returns: The annotation of the given msgspec type.
        """
        annot = cls.get_annotation(msgspec_collection_type.item_type)
        if isinstance(msgspec_collection_type, inspect.ListType):
            return List[annot]  # type: ignore[valid-type]
        if isinstance(msgspec_collection_type, inspect.SetType):
            return Set[annot]  # type: ignore[valid-type]
        if isinstance(msgspec_collection_type, inspect.VarTupleType):
            return Tuple[annot, ...]  # type: ignore[return-value]
        if isinstance(msgspec_collection_type, inspect.FrozenSetType):
            return FrozenSet[annot]  # type: ignore[valid-type]

        raise ParameterException(f"{type(msgspec_collection_type)} is an unsupported CollectionType")

    @classmethod
    def get_annotation(cls, msgspec_type: MsgspecType) -> Type:
        """Return the annotation given a msgspec type.

        :param msgspec_type: A msgspec Type instance.

        :returns: The annotation of the given msgspec type.

        """
        try:
            return cls._MSGSPEC_TYPE_TO_ANNOTATION_MAP[type(msgspec_type)]
        except KeyError:
            pass

        if isinstance(msgspec_type, inspect.CollectionType):
            return cls.get_collection_type_annotation(msgspec_type)
        if isinstance(msgspec_type, inspect.DictType):
            key_annotation = cls.get_annotation(msgspec_type.key_type)
            val_annotation = cls.get_annotation(msgspec_type.value_type)
            return Dict[key_annotation, val_annotation]  # type: ignore[valid-type]
        if isinstance(msgspec_type, inspect.TupleType):
            val_types: list[Type] = [cls.get_annotation(v) for v in msgspec_type.item_types]
            return Tuple[tuple(val_types)]  # type: ignore[return-value]
        if isinstance(
            msgspec_type,
            (
                inspect.EnumType,
                inspect.TypedDictType,
                inspect.NamedTupleType,
                inspect.StructType,
                inspect.CustomType,
            ),
        ):
            return msgspec_type.cls

        raise ParameterException(f"{type(msgspec_type)!r} is an unsupported msgspec type")

    @classmethod
    def parse_field(cls, field: Field) -> FieldMeta:
        """Parse the given msgspec field.

        :param field: A msgspec Field instance.

        :returns: A FieldMeta instance.

        """
        annotation = cls.get_annotation(field.type)
        field_type = field.type
        constraints: Constraints | None = None

        if isinstance(field_type, (inspect.IntType, inspect.FloatType)):
            constraint_names = ["ge", "le", "gt", "lt", "multiple_of"]
            constraints = cls.get_constraints(field_type, constraint_names)

        if isinstance(field_type, (inspect.StrType, inspect.BytesType, inspect.CollectionType, inspect.DictType)):
            constraint_names = ["min_length", "max_length"]
            if isinstance(field_type, inspect.StrType):
                constraint_names.append("pattern")
            constraints = cls.get_constraints(field_type, constraint_names)

        if isinstance(field_type, (inspect.DateTimeType, inspect.TimeType)) and field_type.tz is not None:
            raise ParameterException(f"received constraints for unsupported type {annotation}")

        return FieldMeta.from_type(
            annotation=annotation, name=field.name, constraints=constraints, random=cls.__random__
        )

    @classmethod
    def get_provider_map(cls) -> Dict[Any, Callable[[], Any]]:
        def get_msgpack_ext() -> msgspec.msgpack.Ext:
            code = handle_constrained_int(cls.__random__, ge=-128, le=127)
            data = create_random_bytes(cls.__random__)
            return msgspec.msgpack.Ext(code, data)

        msgpec_provider_map = {msgspec.UnsetType: lambda: msgspec.UNSET, msgspec.msgpack.Ext: get_msgpack_ext}

        provider_map = super().get_provider_map()
        provider_map.update(msgpec_provider_map)

        return provider_map

    @classmethod
    def is_supported_type(cls, value: Any) -> TypeGuard[Type[T]]:
        return isclass(value) and hasattr(value, "__struct_fields__")

    @classmethod
    def get_model_fields(cls) -> List[FieldMeta]:
        type_info = cast(inspect.StructType, inspect.type_info(cls.__model__))

        return [cls.parse_field(f) for f in type_info.fields]
