from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal, Pattern, TypedDict, cast

from polyfactory.constants import DEFAULT_RANDOM, IGNORED_TYPE_ARGS, TYPE_MAPPING
from polyfactory.utils.helpers import normalize_annotation, unwrap_annotated, unwrap_args, unwrap_new_type
from polyfactory.utils.predicates import is_annotated

if TYPE_CHECKING:
    from random import Random

    from _pydecimal import Decimal
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

    constant: NotRequired[bool]
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
    unique_items: NotRequired[bool]
    upper_case: NotRequired[bool]
    url: NotRequired[UrlConstraints]
    uuid_version: NotRequired[Literal[1, 3, 4, 5]]


class FieldMeta:
    """Factory field metadata container. This class is used to store the data about a field of a factory's model."""

    __slots__ = ("name", "annotation", "random", "children", "default", "constraints")

    annotation: Any
    random: Random
    children: list[FieldMeta] | None
    default: Any
    name: str
    constraints: Constraints | None

    def __init__(
        self,
        *,
        name: str,
        annotation: type,
        random: Random = DEFAULT_RANDOM,
        default: Any = Null,
        children: list[FieldMeta] | None = None,
        constraints: Constraints | None = None,
    ):
        """Create a factory field metadata instance."""
        self.annotation = annotation
        self.random = random
        self.children = children
        self.default = default
        self.name = name
        self.constraints = constraints

    @property
    def type_args(self) -> tuple[Any, ...]:
        """Return the normalized type args of the annotation, if any.

        :returns: a tuple of types.
        """
        return tuple(arg for arg in unwrap_args(self.annotation, random=self.random) if arg not in IGNORED_TYPE_ARGS)

    @classmethod
    def from_type(
        cls,
        annotation: Any,
        random: Random = DEFAULT_RANDOM,
        name: str = "",
        default: Any = Null,
        constraints: Constraints | None = None,
    ) -> Self:
        """Builder method to create a FieldMeta from a type annotation.

        :param annotation: A type annotation.
        :param random: An instance of random.Random.
        :param name: Field name
        :param default: Default value, if any.
        :param constraints: A dictionary of constraints, if any.

        :returns: A field meta instance.
        """
        field_type = normalize_annotation(annotation, random=random)

        # FIXME: remove the pragma when switching to pydantic v2 permanently
        if not constraints and is_annotated(annotation):  # pragma: no cover
            _, metadata = unwrap_annotated(field_type, random=random)
            constraints = cls.parse_constraints(metadata)

        field = cls(
            annotation=TYPE_MAPPING[field_type] if field_type in TYPE_MAPPING else field_type,
            random=random,
            name=name,
            default=default,
            children=None,
            constraints=constraints,
        )
        if field.type_args:
            field.children = [
                FieldMeta.from_type(annotation=unwrap_new_type(arg), random=random) for arg in field.type_args
            ]
        return field

    # FIXME: remove the pragma when switching to pydantic v2 permanently
    @classmethod
    def parse_constraints(cls, metadata: list[Any]) -> "Constraints":  # pragma: no cover
        try:
            import annotated_types

            annotated_types_meta_data = [
                ("ge", (annotated_types.Ge, annotated_types.Interval)),
                ("le", (annotated_types.Le, annotated_types.Interval)),
                ("lt", (annotated_types.Lt, annotated_types.Interval)),
                ("gt", (annotated_types.Gt, annotated_types.Interval)),
                ("min_length", (annotated_types.MinLen, annotated_types.Len)),
                ("max_length", (annotated_types.MaxLen, annotated_types.Len)),
                ("multiple_of", annotated_types.MultipleOf),
                # deprecated by pydantic v2
                ("min_items", (annotated_types.MinLen, annotated_types.Len)),
                ("max_items", (annotated_types.MaxLen, annotated_types.Len)),
            ]
        except ImportError:
            annotated_types_meta_data = []

        try:
            from pydantic import UrlConstraints
            from pydantic._internal._fields import PydanticGeneralMetadata
            from pydantic.types import PathType, UuidVersion

            pydantic_annotated_meta_data = [
                ("pattern", PydanticGeneralMetadata),
                ("max_digits", PydanticGeneralMetadata),
                ("decimal_places", PydanticGeneralMetadata),
                # pydantic 2 only constraints
                ("strict", PydanticGeneralMetadata),
                ("allow_inf_nan", PydanticGeneralMetadata),
                ("url", UrlConstraints),
                ("uuid_version", UuidVersion),
                ("path_type", PathType),
            ]
        except ImportError:
            PydanticGeneralMetadata = Null  # type: ignore
            UrlConstraints = Null  # type: ignore
            UuidVersion = Null  # type: ignore
            PathType = Null  # type: ignore
            pydantic_annotated_meta_data = []

        constraints = {}

        for key, annotated_type in [*annotated_types_meta_data, *pydantic_annotated_meta_data]:
            for constraint in metadata:
                if isinstance(constraint, annotated_type):  # type: ignore[arg-type]
                    if isinstance(constraint, PydanticGeneralMetadata):
                        constraints[key] = constraint.__dict__.get(key, None)
                    elif isinstance(constraint, UrlConstraints):
                        constraints[key] = dict(constraint.__dict__)
                    elif isinstance(constraint, UuidVersion):
                        constraints[key] = constraint.uuid_version  # pyright: ignore
                    elif isinstance(constraint, PathType):
                        constraints[key] = constraint.path_type  # pyright: ignore
                    elif key not in ["min_items", "max_items"]:
                        constraints[key] = getattr(constraint, key)
                    else:
                        constraints[key] = getattr(constraint, "min_length" if key == "min_items" else "max_length")
        return cast("Constraints", constraints)
