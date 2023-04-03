from __future__ import annotations
from typing import Any

from polyfactory.constants import TYPE_MAPPING
from polyfactory.utils.helpers import unwrap_args, unwrap_new_type


class Null:
    """Sentinel class for empty values"""


class FieldMeta:
    """Factory field metadata container. This class is used to store the data about a field of a factory's model."""

    __slots__ = ("name", "annotation", "children", "default", "constant")

    annotation: Any
    children: list[FieldMeta] | None
    constant: bool
    default: Any
    name: str

    def __init__(
        self,
        *,
        name: str,
        annotation: type,
        default: Any = Null,
        children: list[FieldMeta] | None = None,
        constant: bool = False,
    ):
        """Create a factory field metadata instance."""
        self.annotation = annotation
        self.children = children
        self.default = default
        self.name = name
        self.constant = constant

    @property
    def type_args(self) -> tuple[Any, ...]:
        """Return the normalized type args of the annotation, if any.

        :returns: a tuple of types.
        """
        return tuple(TYPE_MAPPING[arg] if arg in TYPE_MAPPING else arg for arg in unwrap_args(self.annotation))

    @classmethod
    def from_type(cls, annotation: Any, name: str = "", default: Any = Null) -> FieldMeta:
        """Builder method to create a FieldMeta from a type annotation.

        :param annotation: A type annotation.
        :param name: Field name
        :param default: Default value, if any.

        :returns: A field meta instance.
        """
        field = FieldMeta(
            annotation=unwrap_new_type(annotation),
            name=name,
            default=default,
            constant=False,
            children=None,
        )
        if field.type_args:
            field.children = [FieldMeta.from_type(annotation=unwrap_new_type(arg)) for arg in field.type_args]
        return field
