from __future__ import annotations

import functools
from collections.abc import Hashable
from typing import TYPE_CHECKING, Any, Literal, TypedDict, cast

from typing_extensions import get_args, get_origin

from polyfactory.constants import TYPE_MAPPING
from polyfactory.utils._internal.constraints import parse_constraints
from polyfactory.utils._internal.type_node import TypeNode, parse, with_children
from polyfactory.utils.helpers import (
    get_annotation_metadata,
    unwrap_new_type,
)
from polyfactory.utils.normalize_type import normalize_type
from polyfactory.utils.predicates import is_annotated
from polyfactory.utils.types import NoneType

if TYPE_CHECKING:
    import datetime
    from collections.abc import Sequence
    from decimal import Decimal
    from random import Random
    from re import Pattern

    from typing_extensions import NotRequired, Self


class Null:
    """Sentinel class for empty values"""


class UrlConstraints(TypedDict):
    max_length: NotRequired[int]
    allowed_schemes: NotRequired[list[str]]
    host_required: NotRequired[bool]
    default_host: NotRequired[str]
    default_port: NotRequired[int]
    default_path: NotRequired[str]


class Constraints(TypedDict):
    """Metadata regarding a type constraints, if any"""

    allow_inf_nan: NotRequired[bool]
    decimal_places: NotRequired[int]
    ge: NotRequired[int | float | Decimal]
    gt: NotRequired[int | float | Decimal]
    item_type: NotRequired[Any]
    le: NotRequired[int | float | Decimal]
    lower_case: NotRequired[bool]
    lt: NotRequired[int | float | Decimal]
    max_digits: NotRequired[int]
    max_length: NotRequired[int]
    min_length: NotRequired[int]
    multiple_of: NotRequired[int | float | Decimal]
    path_type: NotRequired[Literal["file", "dir", "new"]]
    pattern: NotRequired[str | Pattern]
    tz: NotRequired[datetime.tzinfo]
    unique_items: NotRequired[bool]
    upper_case: NotRequired[bool]
    url: NotRequired[UrlConstraints]
    uuid_version: NotRequired[Literal[1, 3, 4, 5]]


class FieldMeta:
    """Factory field metadata container. This class is used to store the data about a field of a factory's model."""

    __slots__ = ("__dict__", "annotation", "children", "constraints", "default", "examples", "name", "random")

    annotation: Any
    random: Random
    children: list[FieldMeta] | None
    default: Any
    name: str
    constraints: Constraints | None
    examples: list[Any] | None

    def __init__(
        self,
        *,
        name: str,
        annotation: type,
        default: Any = Null,
        children: list[FieldMeta] | None = None,
        constraints: Constraints | None = None,
        examples: list[Any] | None = None,
        required: bool = True,
    ) -> None:
        """Create a factory field metadata instance."""
        self.annotation = annotation
        self.children = children
        self.default = default
        self.name = name
        self.constraints = constraints
        self.examples = examples
        self.required = required
        # Children passed in by a model integration (e.g. pydantic union members carrying their own constraints) are
        # the source of truth for the parsed type's members. Children derived in ``from_type`` are not.
        self._explicit_children = children is not None

    def __repr__(self) -> str:
        """Return a string representation of the field meta."""
        return f"FieldMeta(name={self.name!r}, annotation={self.annotation!r}, default={self.default!r}, children={self.children!r}, constraints={self.constraints!r})"

    @property
    def _type_node(self) -> TypeNode:
        """The parsed type of this field.

        Parsed on first access and cached. Re-parsed if ``annotation``, ``constraints`` or ``children`` is reassigned,
        as some integrations do after construction.

        :returns: A type node.
        """
        annotation, constraints, children = self.annotation, self.constraints, self.children
        cached = self.__dict__.get("_type_node_cache")
        if cached is not None and cached[0] is annotation and cached[1] is constraints and cached[2] is children:
            return cast("TypeNode", cached[3])

        # Parse the annotation as written - keeping type aliases nominal - unless it was reassigned after construction.
        # Constraints `from_type` read from the annotation itself are already in the parsed node.
        written, normalized, own_constraints = self.__dict__.get("_annotations", (annotation, annotation, None))
        source = written if annotation is normalized else annotation
        node = parse(source, None if constraints is own_constraints and source is written else constraints)
        if self._explicit_children and children:
            node = with_children(node, [child._type_node for child in children])

        self.__dict__["_type_node_cache"] = (annotation, constraints, children, node)
        return node

    @functools.cached_property
    def type_args(self) -> tuple[Any, ...]:
        """Return the normalized type args of the annotation, if any.

        :returns: a tuple of types.
        """
        annotation = self.annotation
        if is_annotated(annotation):
            annotation = get_args(self.annotation)[0]
        return tuple(
            TYPE_MAPPING.get(arg, arg) if isinstance(arg, Hashable) else arg  # type: ignore[call-overload]
            for arg in get_args(annotation)
        )

    @classmethod
    def from_type(
        cls,
        annotation: Any,
        name: str = "",
        default: Any = Null,
        constraints: Constraints | None = None,
        children: list[FieldMeta] | None = None,
        required: bool = True,
        examples: list[Any] | None = None,
    ) -> Self:
        """Builder method to create a FieldMeta from a type annotation.

        :param annotation: A type annotation.
        :param name: Field name
        :param default: Default value, if any.
        :param constraints: A dictionary of constraints, if any.
        :param examples: A list of example values, if any.

        :returns: A field meta instance.
        """
        written_annotation, passed_constraints = annotation, constraints
        annotation = normalize_type(annotation)
        annotated = is_annotated(annotation)
        if not constraints and annotated:
            metadata = cls.get_constraints_metadata(annotation)
            constraints = cls.parse_constraints(metadata)

        if examples is None and annotated:
            examples = cls.parse_examples(get_annotation_metadata(annotation))

        # annotations can take many forms: Optional, an Annotated type, or anything with __args__
        # in order to normalize the annotation, we need to unwrap the annotation.
        if not annotated and (origin := get_origin(annotation)) and origin in TYPE_MAPPING:
            container = TYPE_MAPPING[origin]
            annotation = container[get_args(annotation)]  # type: ignore[index]

        field = cls(
            annotation=annotation,
            name=name,
            default=default,
            children=children,
            constraints=constraints,
            examples=examples,
            required=required,
        )
        field.__dict__["_annotations"] = (
            written_annotation,
            annotation,
            constraints if constraints is not passed_constraints else None,
        )

        if field.type_args and not field.children:
            field.children = [
                cls.from_type(annotation=unwrap_new_type(arg)) for arg in field.type_args if arg is not NoneType
            ]
        return field

    @classmethod
    def parse_constraints(cls, metadata: Sequence[Any]) -> "Constraints":
        """Parse constraints from ``Annotated`` metadata.

        :param metadata: The metadata of an ``Annotated`` annotation.

        :returns: The constraints found in it.
        """
        return parse_constraints(metadata)

    @classmethod
    def parse_examples(cls, metadata: Sequence[Any]) -> list[Any] | None:
        """Get the example values from the given annotation metadata.

        Any metadata object with a non-empty ``examples`` list attribute is supported,
        e.g. ``msgspec.Meta`` or ``pydantic.Field``. If several are given, the last one wins.

        :param metadata: A list of annotation metadata.

        :returns: A list of example values, if any.
        """
        examples = None
        for value in metadata:
            if isinstance(value_examples := getattr(value, "examples", None), list) and value_examples:
                examples = value_examples
        return examples

    @classmethod
    def get_constraints_metadata(cls, annotation: Any) -> Sequence[Any]:
        """Get the metadatas of the constraints from the given annotation.

        :param annotation: A type annotation.
        :param random: An instance of random.Random.

        :returns: A list of the metadata in the annotation.
        """

        return get_annotation_metadata(annotation)
