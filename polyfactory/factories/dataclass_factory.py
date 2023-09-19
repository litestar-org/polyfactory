from __future__ import annotations

from dataclasses import MISSING, fields, is_dataclass
from typing import TYPE_CHECKING, Any, ForwardRef, Generic

from polyfactory.factories.base import BaseFactory, T
from polyfactory.field_meta import FieldMeta, Null
from polyfactory.utils.helpers import evaluate_forwardref

if TYPE_CHECKING:
    from typing_extensions import TypeGuard


class DataclassFactory(Generic[T], BaseFactory[T]):
    """Dataclass base factory"""

    __is_base_factory__ = True

    @classmethod
    def is_supported_type(cls, value: Any) -> TypeGuard[type[T]]:
        """Determine whether the given value is supported by the factory.

        :param value: An arbitrary value.
        :returns: A typeguard
        """
        return bool(is_dataclass(value))

    @classmethod
    def get_model_fields(cls) -> list["FieldMeta"]:
        """Retrieve a list of fields from the factory's model.


        :returns: A list of field MetaData instances.

        """
        fields_meta: list["FieldMeta"] = []

        for field in fields(cls.__model__):  # type: ignore[arg-type]
            if field.default_factory and field.default_factory is not MISSING:
                default_value = field.default_factory()
            elif field.default is not MISSING:
                default_value = field.default
            else:
                default_value = Null

            if isinstance(field.type, ForwardRef):
                annotation = evaluate_forwardref(field.type)  # type: ignore[unreachable]
            elif isinstance(field.type, str):
                annotation = evaluate_forwardref(ForwardRef(field.type))  # type: ignore[unreachable]
            else:
                annotation = field.type

            fields_meta.append(
                FieldMeta.from_type(
                    annotation=annotation,
                    name=field.name,
                    default=default_value,
                    random=cls.__random__,
                    randomize_collection_length=cls.__randomize_collection_length__,
                    min_collection_length=cls.__min_collection_length__,
                    max_collection_length=cls.__max_collection_length__,
                )
            )

        return fields_meta
