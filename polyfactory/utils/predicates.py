from __future__ import annotations

import sys
from inspect import isclass
from typing import Any, Literal, NewType, Optional, TypeVar, Union, get_args

from typing_extensions import (
    Annotated,
    NotRequired,
    ParamSpec,
    Required,
    TypeGuard,
    _AnnotatedAlias,
    get_origin,
)

from polyfactory.constants import TYPE_MAPPING

if sys.version_info >= (3, 10):  # pragma: no cover
    from types import NoneType, UnionType

    UNION_TYPES = {UnionType, Union}
else:  # pragma: no cover
    NoneType = type(None)
    UNION_TYPES = {Union}


P = ParamSpec("P")
T = TypeVar("T")


def is_safe_subclass(annotation: Any, super_class: type[T]) -> "TypeGuard[type[T]]":
    """Determine whether a given annotation is a subclass of a give type

    :param annotation: A type annotation.
    :param super_class: A potential super class.

    :returns: A typeguard
    """
    origin = get_type_origin(annotation)
    if not origin and not isclass(annotation):
        return False
    try:
        return issubclass(origin or annotation, super_class)
    except TypeError:  # pragma: no cover
        return False


def is_any(annotation: Any) -> "TypeGuard[Any]":
    """Determine whether a given annotation is 'typing.Any'.

    :param annotation: A type annotation.

    :returns: A typeguard.
    """
    return (
        annotation is Any
        or getattr(annotation, "_name", "") == "typing.Any"
        or (get_origin(annotation) in UNION_TYPES and Any in get_args(annotation))
    )


def is_union(annotation: Any) -> "TypeGuard[Any | Any]":
    """Determine whether a given annotation is 'typing.Union'.

    :param annotation: A type annotation.

    :returns: A typeguard.
    """
    return get_type_origin(annotation) in UNION_TYPES


def is_optional_union(annotation: Any) -> "TypeGuard[Any | None]":
    """Determine whether a given annotation is 'typing.Optional'.

    :param annotation: A type annotation.

    :returns: A typeguard.
    """
    origin = get_type_origin(annotation)
    return origin is Optional or (get_origin(annotation) in UNION_TYPES and NoneType in get_args(annotation))


def is_literal(annotation: Any) -> bool:
    """Determine whether a given annotation is 'typing.Literal'.

    :param annotation: A type annotation.

    :returns: A boolean.
    """
    return (
        get_type_origin(annotation) is Literal
        or repr(annotation).startswith("typing.Literal")
        or repr(annotation).startswith("typing_extensions.Literal")
    )


def is_new_type(annotation: Any) -> "TypeGuard[type[NewType]]":
    """Determine whether a given annotation is 'typing.NewType'.

    :param annotation: A type annotation.

    :returns: A typeguard.
    """
    return hasattr(annotation, "__supertype__")


def is_annotated(annotation: Any) -> bool:
    """Determine whether a given annotation is 'typing.Annotated'.

    :param annotation: A type annotation.

    :returns: A boolean.
    """
    return get_origin(annotation) is Annotated or (
        isinstance(annotation, _AnnotatedAlias) and getattr(annotation, "__args__", None) is not None
    )


def get_type_origin(annotation: Any) -> Any:
    """Get the type origin of an annotation - safely.

    :param annotation: A type annotation.

    :returns: A type annotation.
    """
    origin = get_origin(annotation)
    if origin in (Annotated, Required, NotRequired):
        origin = get_args(annotation)[0]
    if mapped_type := TYPE_MAPPING.get(origin):  # pyright: ignore
        return mapped_type
    return origin
