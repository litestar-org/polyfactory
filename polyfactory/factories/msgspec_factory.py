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

_MSGSPEC_TYPE_TO_ANNOTATION_MAP: dict[Type[MsgspecType], Type] = {
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


def get_constraints(field_type: inspect.Type, names: Iterable[str]) -> Constraints:
    """Get the constraints on a field type.

    :param t: A msgspec CollectionType.
    :param names: The constraint names.

    :returns: The constraints on the given field type.

    """
    constraints = {}
    for k in names:
        constraint = getattr(field_type, k)
        if constraint is not None:
            constraints[k] = constraint

    return cast(Constraints, constraints)


def get_collection_type_annotation(t: inspect.CollectionType) -> Type:
    """Return the annotation for a msgspec collection type.

    :param t: A msgspec CollectionType.

    :returns: The annotation of the given msgspec type.
    """
    annot = get_annotation(t.item_type)
    if isinstance(t, inspect.ListType):
        return List[annot]  # type: ignore[valid-type]
    if isinstance(t, inspect.SetType):
        return Set[annot]  # type: ignore[valid-type]
    if isinstance(t, inspect.VarTupleType):
        return Tuple[annot, ...]  # type: ignore[return-value]
    if isinstance(t, inspect.FrozenSetType):
        return FrozenSet[annot]  # type: ignore[valid-type]

    msg = f"{type(t)} is an unsupported CollectionType"
    raise ParameterException(msg)


def get_annotation(t: MsgspecType) -> Type:
    """Return the annotation given a msgspec type.

    :param t: A msgspec CollectionType.

    :returns: The annotation of the given msgspec type.

    """
    try:
        return _MSGSPEC_TYPE_TO_ANNOTATION_MAP[type(t)]
    except KeyError:
        pass

    if isinstance(t, inspect.CollectionType):
        return get_collection_type_annotation(t)
    if isinstance(t, inspect.DictType):
        key_annot = get_annotation(t.key_type)
        val_annot = get_annotation(t.value_type)
        return Dict[key_annot, val_annot]  # type: ignore[valid-type]
    if isinstance(t, inspect.TupleType):
        val_types: list[Type] = [get_annotation(v) for v in t.item_types]
        return Tuple[*val_types]  # type: ignore[return-value]
    if isinstance(
        t,
        (
            inspect.EnumType,
            inspect.TypedDictType,
            inspect.NamedTupleType,
            inspect.StructType,
            inspect.CustomType,
        ),
    ):
        return t.cls

    msg = f"{type(t)!r} is an unsupported msgspec type"
    raise ParameterException(msg)


def parse_field(field: Field) -> FieldMeta:
    """Parse the given msgpec field.

    :param field: A msgspec Field instance.

    :returns: A FieldMeta instance.

    """
    annot = get_annotation(field.type)
    field_type = field.type
    constraints: Constraints | None = None

    if isinstance(field_type, (inspect.IntType, inspect.FloatType)):
        constraint_names = ["ge", "le", "gt", "lt", "multiple_of"]
        constraints = get_constraints(field_type, constraint_names)

    if isinstance(field_type, (inspect.StrType, inspect.BytesType, inspect.CollectionType, inspect.DictType)):
        constraint_names = ["min_length", "max_length"]
        if isinstance(field_type, inspect.StrType):
            constraint_names.append("pattern")
        constraints = get_constraints(field_type, constraint_names)

    if isinstance(field_type, (inspect.DateTimeType, inspect.TimeType)) and field_type.tz is not None:
        raise ParameterException(f"received constraints for unsupported type {annot}")

    return FieldMeta.from_type(annot, field.name, constraints=constraints)


class MsgspecFactory(Generic[T], BaseFactory[T]):
    __is_base_factory__ = True

    @classmethod
    def get_provider_map(cls) -> dict[Any, Callable[[], Any]]:
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
    def get_model_fields(cls) -> list[FieldMeta]:
        type_info = cast(inspect.StructType, inspect.type_info(cls.__model__))

        return [parse_field(f) for f in type_info.fields]
