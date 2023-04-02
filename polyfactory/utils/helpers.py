from __future__ import annotations
from typing import Any, get_args

from polyfactory.utils.predicates import (
    is_annotated,
    is_new_type,
    is_optional_union,
    is_union,
)


def unwrap_new_type(annotation: Any) -> Any:
    """Return base type if given annotation is a type derived with NewType, otherwise annotation.

    :param annotation: A type annotation, possibly one created using 'types.NewType'

    :returns: The unwrapped annotation.
    """
    while is_new_type(annotation):
        annotation = annotation.__supertype__

    return annotation


def unwrap_union(annotation: Any) -> Any:
    """Unwraps union types - recursively.

    :param annotation: A type annotation, possibly a type union.
    :returns: A type annotation
    """
    while is_union(annotation):
        annotation = get_args(annotation)[0]
    return annotation


def unwrap_optional(annotation: Any) -> Any:
    """Unwraps optional union types - recursively.

    :param annotation: A type annotation, possibly an optional union.

    :returns: A type annotation
    """
    while is_optional_union(annotation):
        args = get_args(annotation)
        annotation = args[0] if args[0] not in (type(None), None) else args[1]
    return annotation


def unwrap_annotation(annotation: Any) -> Any:
    """Unwraps an annotation.

    :param annotation: A type annotation.

    :returns: The unwrapped annotation.

    """
    while is_optional_union(annotation) or is_union(annotation) or is_new_type(annotation) or is_annotated(annotation):
        if is_new_type(annotation):
            annotation = unwrap_new_type(annotation)
        elif is_optional_union(annotation):
            annotation = unwrap_optional(annotation)
        elif is_annotated(annotation):
            annotation = get_args(annotation)[0]
        else:
            annotation = unwrap_union(annotation)
    return annotation


def unwrap_args(annotation: Any) -> tuple[Any, ...]:
    """Unwrap the annotation and return any type args.

    :param annotation: A type annotation

    :returns: A tuple of type args.

    """

    return get_args(unwrap_annotation(annotation=annotation))
