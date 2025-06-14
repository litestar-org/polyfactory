from __future__ import annotations

import sys
from collections import deque
from dataclasses import is_dataclass
from typing import TYPE_CHECKING, Any, Mapping, Sequence

from typing_extensions import get_args, get_origin

from polyfactory.constants import TYPE_MAPPING
from polyfactory.utils.deprecation import check_for_deprecated_parameters, deprecated
from polyfactory.utils.predicates import (
    is_annotated,
    is_new_type,
    is_optional,
    is_safe_subclass,
    is_type_alias,
    is_union,
)
from polyfactory.utils.types import NoneType

if TYPE_CHECKING:
    from random import Random


def unwrap_new_type(annotation: Any) -> Any:
    """Return base type if given annotation is a type derived with NewType, otherwise annotation.

    :param annotation: A type annotation, possibly one created using 'types.NewType'

    :returns: The unwrapped annotation.
    """
    while is_new_type(annotation):
        annotation = annotation.__supertype__

    return annotation


@deprecated("v2.21.0")
def unwrap_union(annotation: Any, random: Random) -> Any:
    """Unwraps union types recursively and picks a random type from each union.

    :param annotation: A type annotation, possibly a type union.
    :param random: An instance of random.Random.
    :returns: A type annotation
    """
    while is_union(annotation):
        args = list(get_args(annotation))
        annotation = random.choice(args)
    return annotation


def unwrap_optional(annotation: Any) -> Any:
    """Unwraps optional union types - recursively.

    :param annotation: A type annotation, possibly an optional union.

    :returns: A type annotation
    """
    while is_optional(annotation):
        annotation = next(arg for arg in get_args(annotation) if arg not in (NoneType, None))
    return annotation


def unwrap_annotation(annotation: Any, random: Random | None = None) -> Any:
    """Unwraps an annotation.

    :param annotation: A type annotation.
    :param random: An instance of random.Random.

    :returns: The unwrapped annotation.

    """
    check_for_deprecated_parameters("2.21.0", parameters=(("random", random),))
    while is_optional(annotation) or is_new_type(annotation) or is_annotated(annotation) or is_type_alias(annotation):
        if is_new_type(annotation):
            annotation = unwrap_new_type(annotation)
        elif is_optional(annotation):
            annotation = unwrap_optional(annotation)
        elif is_annotated(annotation):
            annotation = unwrap_annotated(annotation)[0]
        elif is_type_alias(annotation):
            annotation = annotation.__value__

    return annotation


def flatten_annotation(annotation: Any) -> list[Any]:
    """Flattens an annotation into an array of possible types. For example:

    * Union[str, int] → [str, int]
    * Optional[str] → [str, None]
    * Union[str, Optional[int]] → [str, int, None]
    * NewType('UserId', int) → [int]

    :param annotation: A type annotation.

    :returns: The flattened annotations.
    """
    flat = []
    if is_new_type(annotation):
        flat.extend(flatten_annotation(unwrap_new_type(annotation)))
    elif is_optional(annotation):
        for a in get_args(annotation):
            flat.extend(flatten_annotation(a))
    elif is_annotated(annotation):
        flat.extend(flatten_annotation(get_args(annotation)[0]))
    elif is_union(annotation):
        for a in get_args(annotation):
            flat.extend(flatten_annotation(a))
    else:
        flat.append(annotation)

    return flat


def unwrap_args(annotation: Any, random: Random | None = None) -> tuple[Any, ...]:
    """Unwrap the annotation and return any type args.

    :param annotation: A type annotation
    :param random: An instance of random.Random.

    :returns: A tuple of type args.

    """
    check_for_deprecated_parameters("2.21.0", parameters=(("random", random),))
    return get_args(unwrap_annotation(annotation=annotation))


def unwrap_annotated(annotation: Any, random: Random | None = None) -> tuple[Any, list[Any]]:
    """Unwrap an annotated type and return a tuple of type args and optional metadata.

    :param annotation: An annotated type annotation
    :param random: An instance of random.Random.

    :returns: A tuple of type args.

    """
    check_for_deprecated_parameters("2.21.0", parameters=(("random", random),))
    args = [arg for arg in get_args(annotation) if arg is not None]
    return unwrap_annotation(args[0]), args[1:]


def normalize_annotation(annotation: Any, random: Random | None = None) -> Any:
    """Normalize an annotation.

    :param annotation: A type annotation.

    :returns: A normalized type annotation.

    """
    check_for_deprecated_parameters("2.21.0", parameters=(("random", random),))

    if is_new_type(annotation):
        annotation = unwrap_new_type(annotation)

    if is_annotated(annotation):
        annotation = unwrap_annotated(annotation)[0]

    # we have to maintain compatibility with the older non-subscriptable typings.
    if sys.version_info < (3, 9):  # pragma: no cover
        return annotation

    origin = get_origin(annotation) or annotation

    if origin in TYPE_MAPPING:
        origin = TYPE_MAPPING[origin]

    if args := get_args(annotation):
        args = tuple(normalize_annotation(arg) for arg in args)
        return origin[args] if origin is not type else annotation

    return origin


def get_annotation_metadata(annotation: Any) -> Sequence[Any]:
    """Get the metadata in the annotation.

    :param annotation: A type annotation.

    :returns: The metadata.
    """

    return get_args(annotation)[1:]


def get_collection_type(annotation: Any) -> type[list | tuple | set | frozenset | dict | deque]:  # noqa: PLR0911
    """Get the collection type from the annotation.

    :param annotation: A type annotation.

    :returns: The collection type.
    """

    if is_safe_subclass(annotation, list):
        return list
    if is_safe_subclass(annotation, Mapping):
        return dict
    if is_safe_subclass(annotation, tuple):
        return tuple
    if is_safe_subclass(annotation, set):
        return set
    if is_safe_subclass(annotation, frozenset):
        return frozenset
    if is_safe_subclass(annotation, deque):
        return deque
    if is_safe_subclass(annotation, Sequence):
        return list

    msg = f"Unknown collection type - {annotation}"
    raise ValueError(msg)


def is_dataclass_instance(obj: Any) -> bool:
    return is_dataclass(obj) and not isinstance(obj, type)
