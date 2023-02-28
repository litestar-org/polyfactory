from typing import Any, Dict, List, Optional, Tuple, Type

from typing_extensions import get_args

from polyfactory.constants import TYPE_MAPPING
from polyfactory.utils.helpers import unwrap_new_type
from polyfactory.utils.predicates import get_type_origin


class Null:
    pass


class FieldMeta:
    __slots__ = ("name", "annotation", "children", "default", "constant", "extra")

    annotation: Any
    children: Optional[List["FieldMeta"]]
    constant: bool
    default: Any
    extra: Any
    name: str

    def __init__(
        self,
        *,
        name: str,
        annotation: Type,
        default: Any = Null,
        children: Optional[List["FieldMeta"]] = None,
        constant: bool = False,
        extra: Optional[Dict[str, Any]],
    ):
        self.annotation = annotation
        self.children = children
        self.default = default
        self.name = name
        self.constant = constant
        self.extra = extra

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
        return tuple(TYPE_MAPPING[arg] if arg in TYPE_MAPPING else arg for arg in get_args(self.annotation))

    @classmethod
    def from_type(cls, annotation: Any, name: str = "", default: Any = Null, **kwargs: Any) -> "FieldMeta":
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
            extra=kwargs,
        )
        if field.type_args:
            field.children = [FieldMeta.from_type(annotation=unwrap_new_type(arg)) for arg in field.type_args]
        return field
