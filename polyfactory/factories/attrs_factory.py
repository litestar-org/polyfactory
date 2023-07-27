from __future__ import annotations

from inspect import isclass
from typing import TYPE_CHECKING, TypeVar

from polyfactory.exceptions import MissingDependencyException
from polyfactory.factories.base import BaseFactory
from polyfactory.field_meta import FieldMeta, Null

if TYPE_CHECKING:
    from typing import Any, TypeGuard


try:
    import attrs
    from attr._make import Factory
except ImportError as ex:
    raise MissingDependencyException("attrs is not installed") from ex

T = TypeVar("T", bound=attrs.AttrsInstance)


class AttrsFactory(BaseFactory[T]):
    """Base factory for attrs classes."""

    __is_base_factory__ = True

    @classmethod
    def is_supported_type(cls, value: Any) -> TypeGuard[type[T]]:
        return isclass(value) and hasattr(value, "__attrs_attrs__")

    @classmethod
    def get_model_fields(cls) -> list[FieldMeta]:
        field_metas: list[FieldMeta] = []
        fields = attrs.fields(cls.__model__)
        none_type = type(None)

        for field in fields:
            annotation = none_type if field.type is None else field.type

            default = field.default
            if isinstance(default, Factory):
                # The default value is not currently being used when generating
                # the field values. When that is implemented, this would need
                # to be handled differently since the `default.factory` could
                # take a `self` argument.
                default_value = default.factory
            elif default is None:
                default_value = Null
            else:
                default_value = default

            field_metas.append(
                FieldMeta.from_type(
                    annotation=annotation,
                    name=field.alias,
                    default=default_value,
                    random=cls.__random__,
                    randomize_collection_length=cls.__randomize_collection_length__,
                    min_collection_length=cls.__min_collection_length__,
                    max_collection_length=cls.__max_collection_length__,
                )
            )

        return field_metas
