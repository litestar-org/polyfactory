import sys
from inspect import isclass
from typing import Any, Literal, NewType, Optional, Type, TypeVar, Union, get_args

from typing_extensions import (
    Annotated,
    NotRequired,
    ParamSpec,
    Required,
    TypeGuard,
    get_origin,
)

from polyfactory.constants import TYPE_MAPPING

if sys.version_info >= (3, 10):
    from types import NoneType, UnionType

    UNION_TYPES = {UnionType, Union}
else:  # pragma: no cover
    NoneType = type(None)
    UNION_TYPES = {Union}


P = ParamSpec("P")
T = TypeVar("T")


def is_safe_subclass(value: Any, types: Type[T]) -> TypeGuard[Type[T]]:
    """

    :param value:
    :param types:
    :return:
    """
    origin = get_type_origin(value)
    if not origin and not isclass(value):
        return False
    try:
        return issubclass(origin or value, types)
    except TypeError:  # pragma: no cover
        return False


def is_any(annotation: Any) -> "TypeGuard[Any]":
    """Given a type annotation determine if the annotation is Any.

        Args:
        annotation: A type.

    Returns:
        A typeguard determining whether the type is :data:`Any <typing.Any>`.
    """
    return (
        annotation is Any
        or getattr(annotation, "_name", "") == "typing.Any"
        or (get_origin(annotation) in UNION_TYPES and Any in get_args(annotation))
    )


def is_union(annotation: Any) -> "TypeGuard[Union[Any, Any]]":
    """Given a type annotation determine if the annotation infers an optional union.

    Args:
        annotation: A type.

    Returns:
        A typeguard determining whether the type is :data:`Union typing.Union>`.
    """
    return get_type_origin(annotation) in UNION_TYPES


def is_optional_union(annotation: Any) -> "TypeGuard[Union[Any, None]]":
    """Given a type annotation determine if the annotation infers an optional union.

    Args:
        annotation: A type.

    Returns:
        A typeguard determining whether the type is :data:`Union typing.Union>` with a
            None value or :data:`Optional <typing.Optional>` which is equivalent.
    """
    origin = get_type_origin(annotation)
    return origin is Optional or (get_origin(annotation) in UNION_TYPES and NoneType in get_args(annotation))


def is_literal(value: Any) -> bool:
    """Determines whether a given model_field is a Literal type."""
    return (
        get_type_origin(value) is Literal
        or repr(value).startswith("typing.Literal")
        or repr(value).startswith("typing_extensions.Literal")
    )


def is_new_type(value: Any) -> "TypeGuard[Type[NewType]]":
    """

    :param value:
    :return:
    """
    return hasattr(value, "__supertype__")


def get_type_origin(annotation: Any) -> Any:
    """

    :param annotation:
    :return:
    """
    origin = get_origin(annotation)
    if origin in (Annotated, Required, NotRequired):
        origin = get_args(annotation)[0]
    if mapped_type := TYPE_MAPPING.get(origin):  # pyright: ignore
        return mapped_type
    return origin
