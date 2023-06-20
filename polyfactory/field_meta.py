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
    allow_inf_nan: NotRequired[bool]
    strict: NotRequired[bool]


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
        constraints = {}

        for value in metadata:
            if is_annotated(value):
                _, inner_metadata = unwrap_annotated(value, random=DEFAULT_RANDOM)
                constraints.update(cast("dict[str, Any]", cls.parse_constraints(metadata=inner_metadata)))
            elif func := getattr(value, "func", None):
                if func == str.islower:
                    constraints.update({"lower_case": True})
                if func == str.isupper:
                    constraints.update({"upper_case": True})
                if func == str.isascii:
                    constraints.update({"pattern": "[[:ascii:]]"})
                if func == str.isdigit:
                    constraints.update({"pattern": "[[:digit:]]"})
            elif allowed_schemas := getattr(value, "allowed_schemas", None):
                constraints.update(
                    {
                        "url": {
                            k: v
                            for k, v in {
                                "max_length": getattr(value, "max_length", None),
                                "allowed_schemes": allowed_schemas,
                                "host_required": getattr(value, "host_required", None),
                                "default_host": getattr(value, "default_host", None),
                                "default_port": getattr(value, "default_port", None),
                                "default_path": getattr(value, "default_path", None),
                            }.items()
                            if v is not None
                        }
                    }
                )
            else:
                constraints.update(
                    {
                        k: v
                        for k, v in {
                            "decimal_places": getattr(value, "decimal_places", None),
                            "item_type": getattr(value, "item_type", None),
                            "max_digits": getattr(value, "max_digits", None),
                            "path_type": getattr(value, "path_type", None),
                            "unique_items": getattr(value, "unique_items", None),
                            "uuid_version": getattr(value, "uuid_version", None),
                            "allow_inf_nan": getattr(value, "allow_inf_nan", None),
                            "strict": getattr(value, "strict", None),
                            "gt": getattr(value, "gt", None),
                            "ge": getattr(value, "ge", None),
                            "lt": getattr(value, "lt", None),
                            "le": getattr(value, "le", None),
                            "multiple_of": getattr(value, "multiple_of", None),
                            "min_length": getattr(value, "min_length", getattr(value, "min_items", None)),
                            "max_length": getattr(value, "max_length", getattr(value, "max_length", None)),
                            "lower_case": getattr(value, "to_lower", None),
                            "upper_case": getattr(value, "to_upper", None),
                            "pattern": getattr(value, "regex", getattr(value, "pattern", None)),
                            "constant": getattr(value, "const", None) is not None,
                        }.items()
                        if v is not None
                    }
                )
        return cast("Constraints", constraints)
