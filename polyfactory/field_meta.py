from typing import Any, List, Optional, Tuple, Type

from polyfactory.constants import TYPE_MAPPING
from polyfactory.utils.helpers import unwrap_args, unwrap_new_type
from polyfactory.utils.predicates import get_type_origin


class Null:
    pass


class FieldMeta:
    __slots__ = ("name", "annotation", "children", "default", "constant")

    annotation: Any
    children: Optional[List["FieldMeta"]]
    constant: bool
    default: Any
    name: str

    def __init__(
        self,
        *,
        name: str,
        annotation: Type,
        default: Any = Null,
        children: Optional[List["FieldMeta"]] = None,
        constant: bool = False,
    ):
        self.annotation = annotation
        self.children = children
        self.default = default
        self.name = name
        self.constant = constant

    @property
    def origin(self) -> Any:
        """

        :return:
        """
        return get_type_origin(self.annotation)

    @property
    def type_args(self) -> Tuple[Any, ...]:
        """

        :return:
        """
        return tuple(TYPE_MAPPING[arg] if arg in TYPE_MAPPING else arg for arg in unwrap_args(self.annotation))

    @classmethod
    def from_type(cls, annotation: Any, name: str = "", default: Any = Null) -> "FieldMeta":
        """

        :param annotation:
        :param name:
        :param default:
        :param kwargs:
        :return:
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
