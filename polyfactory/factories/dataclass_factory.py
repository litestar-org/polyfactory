from __future__ import annotations
from dataclasses import is_dataclass, fields, MISSING
from inspect import isclass
from typing import Generic, Any, TYPE_CHECKING


from polyfactory.factories.base import T, BaseFactory
from polyfactory.field_meta import FieldMeta, Null


if TYPE_CHECKING:
    from typing_extensions import TypeGuard


class DataclassFactory(Generic[T], BaseFactory[T]):
    """Dataclass base factory"""

    __is_base_factory__ = True

    @classmethod
    def is_supported_type(cls, value: Any) -> "TypeGuard[type[T]]":
        """Determine whether the given value is supported by the factory.

        :param value: An arbitrary value.
        :returns: A typeguard
        """
        try:
            return isclass(value) and is_dataclass(value)
        except (TypeError, AttributeError):  # pragma: no cover
            return False

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

            fields_meta.append(FieldMeta.from_type(annotation=field.type, name=field.name, default=default_value))

        return fields_meta
