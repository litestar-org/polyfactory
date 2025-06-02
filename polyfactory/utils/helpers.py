from __future__ import annotations

import sys
from collections import deque
from dataclasses import is_dataclass
from typing import TYPE_CHECKING, Annotated, Any, Mapping, Sequence, TypeVar, Union

from typing_extensions import TypeAliasType, get_args, get_origin

from polyfactory.constants import TYPE_MAPPING
from polyfactory.utils.deprecation import check_for_deprecated_parameters, deprecated
from polyfactory.utils.predicates import (
    is_annotated,
    is_generic_alias,
    is_new_type,
    is_optional,
    is_safe_subclass,
    is_type_alias,
    is_type_var,
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
    """Unwraps union types - recursively.

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
    """Flattens an annotation.

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


def resolve_type_alias(type_hint: Any) -> Any:
    """Convert TypeAliasType and GenericAlias to standard annotations.

    Example:
        ```
        # Required Python version >=3.13
        >> from typing import Annotated

        >> import annotated_types as at

        >> from polyfactory.utils.helpers import resolve_type_alias

        >> type NegativeInt = Annotated[int, annotated_types.Lt(0)]
        >> type NonEmptyList[T] = Annotated[list[T], annotated_types.Len(1)]
        >> resolve_type_alias(NonEmptyList[NegativeInt])  # typing.Annotated[list[typing.Annotated[int, Lt(lt=0)]], Len(min_length=1, max_length=None)]
        >> resolve_type_alias(NonEmptyList[NonEmptyList[NegativeInt]])

        # Recursive type annotation
        # typing.Annotated[list[typing.Annotated[list[typing.Annotated[int, Lt(lt=0)]], Len(min_length=1, max_length=None)]], Len(min_length=1, max_length=None)]
        ```

    :param type_hint: Type to convert.

    :returns Expanded type annotation with substituted parameters.
    """
    if is_type_alias(type_hint):
        return type_hint.__value__

    if not is_generic_alias(type_hint):
        return type_hint

    origin = get_origin(type_hint)

    if is_type_alias(origin):
        return _process_generic_alias(origin, type_hint)

    args = get_args(type_hint)
    if args:
        resolved_args = [resolve_type_alias(arg) for arg in args]
        if resolved_args != list(args):
            return origin[*resolved_args]   # type: ignore[index]

    return type_hint


def _process_generic_alias(origin: TypeAliasType, type_hint: Any) -> Any:
    """Process GenericAlias with TypeAliasType."""
    template = origin.__value__

    type_params = origin.__type_params__
    type_args = get_args(type_hint)

    if not (type_params and type_args):
        return template

    resolved_args = [resolve_type_alias(arg) for arg in type_args]

    subs = dict(zip(type_params, resolved_args))

    if get_origin(template) is Annotated:
        base_type, *metadata = get_args(template)
        return Annotated[_substitute_types(base_type, subs), *metadata]

    return _substitute_types(template, subs)


def _substitute_types(type_hint: Any, subs: dict[TypeVar, Any]) -> Any:
    """Recursively substitute TypeVar in type.

    Args:
        type_hint: Type to process.
        subs: Dictionary of TypeVar -> concrete type substitutions.

    Returns:
        Type with substituted values.
    """
    if is_type_var(type_hint):
        return subs.get(type_hint, type_hint)

    if is_union(type_hint):
        args = tuple([_substitute_types(arg, subs) for arg in get_args(type_hint)])
        return Union[*args]

    origin = get_origin(type_hint)
    args = get_args(type_hint)

    if origin and args:
        substituted_args = [_substitute_types(arg, subs) for arg in args]
        return origin[*substituted_args]

    return type_hint
