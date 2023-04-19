from __future__ import annotations

from typing import Any, TypedDict, Pattern, TYPE_CHECKING

from polyfactory.constants import TYPE_MAPPING, IGNORED_TYPE_ARGS
from polyfactory.utils.helpers import unwrap_args, unwrap_new_type

if TYPE_CHECKING:
    from _pydecimal import Decimal
    from typing_extensions import NotRequired


class Null:
    """Sentinel class for empty values"""


class Constraints(TypedDict):
    """Metadata regarding a type constraints, if any"""

    constant: NotRequired[bool]
    decimal_places: NotRequired[int]
    ge: NotRequired[int | float | Decimal]
    gt: NotRequired[int | float | Decimal]
    le: NotRequired[int | float | Decimal]
    lower_case: NotRequired[bool]
    lt: NotRequired[int | float | Decimal]
    max_digits: NotRequired[int]
    max_length: NotRequired[int]
    min_length: NotRequired[int]
    multiple_of: NotRequired[int | float | Decimal]
    pattern: NotRequired[str | Pattern]
    unique_items: NotRequired[bool]
    upper_case: NotRequired[bool]
    item_type: NotRequired[Any]


class FieldMeta:
    """Factory field metadata container. This class is used to store the data about a field of a factory's model."""

    __slots__ = ("name", "annotation", "children", "default", "constraints")

    annotation: Any
    children: list[FieldMeta] | None
    default: Any
    name: str
    constraints: Constraints | None

    def __init__(
        self,
        *,
        name: str,
        annotation: type,
        default: Any = Null,
        children: list[FieldMeta] | None = None,
        constraints: Constraints | None = None,
    ):
        """Create a factory field metadata instance."""
        self.annotation = unwrap_new_type(annotation)
        self.children = children
        self.default = default
        self.name = name
        self.constraints = constraints

    @property
    def type_args(self) -> tuple[Any, ...]:
        """Return the normalized type args of the annotation, if any.

        :returns: a tuple of types.
        """
        return tuple(
            TYPE_MAPPING[arg] if arg in TYPE_MAPPING else arg
            for arg in unwrap_args(self.annotation)
            if arg not in IGNORED_TYPE_ARGS
        )

    @classmethod
    def from_type(
        cls, annotation: Any, name: str = "", default: Any = Null, constraints: Constraints | None = None
    ) -> FieldMeta:
        """Builder method to create a FieldMeta from a type annotation.

        :param annotation: A type annotation.
        :param name: Field name
        :param default: Default value, if any.

        :returns: A field meta instance.
        """
        field = FieldMeta(
            annotation=unwrap_new_type(annotation), name=name, default=default, children=None, constraints=constraints
        )
        if field.type_args:
            field.children = [FieldMeta.from_type(annotation=unwrap_new_type(arg)) for arg in field.type_args]
        return field
