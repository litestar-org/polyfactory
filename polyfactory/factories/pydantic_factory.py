from __future__ import annotations
from contextlib import suppress
from inspect import isclass
from typing import (
    TYPE_CHECKING,
    Any,
    ClassVar,
    Generic,
    Mapping,
    TypeVar,
    cast,
)

from polyfactory.exceptions import MissingDependencyException
from polyfactory.factories.base import BaseFactory
from polyfactory.field_meta import FieldMeta, Null, Constraints
from polyfactory.utils.helpers import unwrap_new_type

try:
    from pydantic import (
        BaseModel,
    )
    from pydantic.fields import DeferredType, ModelField, Undefined
except ImportError as e:
    raise MissingDependencyException("pydantic is not installed") from e


if TYPE_CHECKING:
    from typing_extensions import TypeGuard

T = TypeVar("T", bound=BaseModel)


def is_pydantic_model(value: Any) -> "TypeGuard[type[BaseModel]]":
    """Determine whether the given value is a subclass of BaseModel.

    :param value: A value to test.

    :returns: A type guard.

    """
    try:
        return isclass(value) and issubclass(value, BaseModel)
    except TypeError:  # pragma: no cover
        # isclass(value) returns True for python 3.9+ typings such as list[str] etc.
        # this raises a TypeError in issubclass, and so we need to handle it.
        return False


class PydanticFieldMeta(FieldMeta):
    """Field meta subclass capable of handling pydantic ModelFields"""

    @classmethod
    def from_model_field(cls, model_field: ModelField, use_alias: bool) -> PydanticFieldMeta:
        """Create an instance from a pydantic model field.

        :param model_field: A pydantic ModelField.
        :param use_alias: Whether to use the field alias.

        :returns: A PydanticFieldMeta instance.

        """
        if callable(model_field.default_factory):
            default_value = model_field.default_factory()
        else:
            default_value = model_field.default if model_field.default is not Undefined else Null

        name = model_field.alias if model_field.alias and use_alias else model_field.name

        annotation = unwrap_new_type(
            model_field.annotation if not isinstance(model_field.annotation, DeferredType) else model_field.outer_type_
        )

        constraints = cast(
            "Constraints",
            {
                "constant": bool(model_field.field_info.const) or None,
                "ge": getattr(annotation, "ge", model_field.field_info.ge),
                "gt": getattr(annotation, "gt", model_field.field_info.gt),
                "le": getattr(annotation, "le", model_field.field_info.le),
                "lt": getattr(annotation, "lt", model_field.field_info.lt),
                "min_length": getattr(annotation, "min_length", model_field.field_info.min_length)
                or getattr(annotation, "min_items", model_field.field_info.min_items),
                "max_length": getattr(annotation, "max_length", model_field.field_info.max_length)
                or getattr(annotation, "max_items", model_field.field_info.max_items),
                "pattern": getattr(annotation, "regex", model_field.field_info.regex),
                "unique_items": getattr(annotation, "unique_items", model_field.field_info.unique_items),
                "decimal_places": getattr(annotation, "decimal_places", None),
                "max_digits": getattr(annotation, "max_digits", None),
                "multiple_of": getattr(annotation, "multiple_of", None),
                "upper_case": getattr(annotation, "to_upper", None),
                "lower_case": getattr(annotation, "to_lower", None),
                "item_type": getattr(annotation, "item_type", None),
            },
        )

        return PydanticFieldMeta(
            name=name,
            annotation=annotation,
            children=[
                PydanticFieldMeta.from_model_field(child, use_alias=use_alias) for child in model_field.sub_fields
            ]
            if model_field.sub_fields
            else None,
            default=default_value,
            constraints=cast("Constraints", {k: v for k, v in constraints.items() if v is not None}) or None,
        )


class ModelFactory(Generic[T], BaseFactory[T]):
    """Base factory for pydantic models"""

    __forward_ref_resolution_type_mapping__: ClassVar[Mapping[str, type]] = {}

    def __init_subclass__(cls, *args: Any, **kwargs: Any) -> None:
        super().__init_subclass__(*args, **kwargs)

        if hasattr(cls, "__model__") and hasattr(cls.__model__, "update_forward_refs"):
            with suppress(NameError):  # pragma: no cover
                cls.__model__.update_forward_refs(**cls.__forward_ref_resolution_type_mapping__)

    @classmethod
    def is_supported_type(cls, value: Any) -> "TypeGuard[type[T]]":
        """Determine whether the given value is supported by the factory.

        :param value: An arbitrary value.
        :returns: A typeguard
        """
        return is_pydantic_model(value)

    @classmethod
    def get_model_fields(cls) -> list["FieldMeta"]:
        """Retrieve a list of fields from the factory's model.


        :returns: A list of field MetaData instances.

        """
        if not hasattr(cls, "_fields_metadata"):
            cls._fields_metadata = [
                PydanticFieldMeta.from_model_field(
                    field,
                    use_alias=not cls.__model__.__config__.allow_population_by_field_name,
                )
                for field in cls.__model__.__fields__.values()
            ]
        return cls._fields_metadata

    @classmethod
    def build(cls, factory_use_construct: bool = False, **kwargs: Any) -> T:
        """Build an instance of the factory's __model__

        :param factory_use_construct: A boolean that determines whether validations will be made when instantiating the
                model. This is supported only for pydantic models.
        :param kwargs: Any kwargs. If field_meta names are set in kwargs, their values will be used.

        :returns: An instance of type T.

        """
        processed_kwargs = cls.process_kwargs(**kwargs)

        if factory_use_construct:
            return cls.__model__.construct(**processed_kwargs)

        return cls.__model__(**processed_kwargs)
