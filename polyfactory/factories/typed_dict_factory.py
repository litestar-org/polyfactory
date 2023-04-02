from __future__ import annotations
from typing import TypeVar, Generic, Any
from typing_extensions import TypeGuard, is_typeddict, _TypedDictMeta  # type: ignore[attr-defined]

from polyfactory.factories.base import BaseFactory
from polyfactory.field_meta import FieldMeta, Null

TypedDictT = TypeVar("TypedDictT", bound=_TypedDictMeta)


class TypedDictFactory(Generic[TypedDictT], BaseFactory[TypedDictT]):
    """TypedDict base factory"""

    __is_base_factory__ = True

    @classmethod
    def is_supported_type(cls, value: Any) -> "TypeGuard[type[TypedDictT]]":
        """Determine whether the given value is supported by the factory.

        :param value: An arbitrary value.
        :returns: A typeguard
        """
        try:
            return is_typeddict(value)
        except (TypeError, AttributeError):  # pragma: no cover
            return False

    @classmethod
    def get_model_fields(cls) -> list["FieldMeta"]:
        """Retrieve a list of fields from the factory's model.


        :returns: A list of field MetaData instances.

        """
        fields_meta: list["FieldMeta"] = []

        for field_name, annotation in cls.__model__.__annotations__.items():
            fields_meta.append(
                FieldMeta.from_type(
                    annotation=annotation,
                    name=field_name,
                    default=getattr(cls.__model__, field_name, Null),
                )
            )
        return fields_meta
