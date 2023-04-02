from __future__ import annotations
from contextlib import suppress
from inspect import isclass
from typing import (
    TYPE_CHECKING,
    Any,
    ClassVar,
    Generic,
    Mapping,
    Optional,
    TypeVar,
    cast,
)

from polyfactory.exceptions import MissingDependencyException
from polyfactory.factories.base import BaseFactory
from polyfactory.field_meta import FieldMeta, Null
from polyfactory.utils.helpers import unwrap_new_type
from polyfactory.utils.predicates import is_safe_subclass
from polyfactory.value_generators.constrained_collections import (
    handle_constrained_collection,
)
from polyfactory.value_generators.constrained_dates import handle_constrained_date
from polyfactory.value_generators.constrained_numbers import (
    handle_constrained_decimal,
    handle_constrained_float,
    handle_constrained_int,
)
from polyfactory.value_generators.constrained_strings import handle_constrained_string_or_bytes

try:
    from pydantic import (
        BaseModel,
        ConstrainedBytes,
        ConstrainedDate,
        ConstrainedDecimal,
        ConstrainedFloat,
        ConstrainedFrozenSet,
        ConstrainedInt,
        ConstrainedList,
        ConstrainedSet,
        ConstrainedStr,
    )
    from pydantic.fields import DeferredType, ModelField, Undefined
except ImportError as e:
    raise MissingDependencyException("pydantic is not installed") from e


if TYPE_CHECKING:
    from decimal import Decimal

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
    def from_model_field(cls, model_field: "ModelField", use_alias: bool) -> "PydanticFieldMeta":
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

        annotation = (
            model_field.annotation if not isinstance(model_field.annotation, DeferredType) else model_field.outer_type_
        )

        return PydanticFieldMeta(
            name=name,
            annotation=unwrap_new_type(annotation),
            children=[
                PydanticFieldMeta.from_model_field(child, use_alias=use_alias) for child in model_field.sub_fields
            ]
            if model_field.sub_fields
            else None,
            default=default_value,
            constant=bool(model_field.field_info.const),
        )


class ModelFactory(Generic[T], BaseFactory[T]):
    """Base factory for pydantic models"""

    __forward_ref_resolution_type_mapping__: ClassVar[Mapping[str, type]] = {}
    __is_base_factory__ = True

    def __init_subclass__(cls, *args: Any, **kwargs: Any) -> None:
        super().__init_subclass__(*args, **kwargs)

        if not cls.__is_base_factory__ and hasattr(cls.__model__, "update_forward_refs"):
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
    def get_field_value(cls, field_meta: "FieldMeta", field_build_parameters: Any | None = None) -> Any:
        """Return a field value on the subclass if existing, otherwise returns a mock value.

        :param field_meta: Field metadata.
        :param field_build_parameters: Any build parameters passed to the factory as kwarg values.

        :returns: An arbitrary value.

        """
        if is_safe_subclass(field_meta.annotation, ConstrainedFloat):
            return handle_constrained_float(
                random=cls.__random__,
                multiple_of=field_meta.annotation.multiple_of,
                gt=field_meta.annotation.gt,
                ge=field_meta.annotation.ge,
                lt=field_meta.annotation.lt,
                le=field_meta.annotation.le,
            )

        if is_safe_subclass(field_meta.annotation, ConstrainedInt):
            return handle_constrained_int(
                random=cls.__random__,
                multiple_of=field_meta.annotation.multiple_of,
                gt=field_meta.annotation.gt,
                ge=field_meta.annotation.ge,
                lt=field_meta.annotation.lt,
                le=field_meta.annotation.le,
            )

        if is_safe_subclass(field_meta.annotation, ConstrainedDecimal):
            return handle_constrained_decimal(
                random=cls.__random__,
                decimal_places=field_meta.annotation.decimal_places,
                max_digits=field_meta.annotation.max_digits,
                multiple_of=cast("Optional[Decimal]", field_meta.annotation.multiple_of),
                gt=cast("Optional[Decimal]", field_meta.annotation.gt),
                ge=cast("Optional[Decimal]", field_meta.annotation.ge),
                lt=cast("Optional[Decimal]", field_meta.annotation.lt),
                le=cast("Optional[Decimal]", field_meta.annotation.le),
            )

        if is_safe_subclass(field_meta.annotation, ConstrainedStr) or is_safe_subclass(
            field_meta.annotation, ConstrainedBytes
        ):
            return handle_constrained_string_or_bytes(
                random=cls.__random__,
                t_type=str if is_safe_subclass(field_meta.annotation, ConstrainedStr) else bytes,
                lower_case=field_meta.annotation.to_lower,
                upper_case=field_meta.annotation.to_lower,
                min_length=field_meta.annotation.min_length,
                max_length=field_meta.annotation.max_length,
                pattern=getattr(field_meta.annotation, "regex", None),
            )

        if (
            is_safe_subclass(field_meta.annotation, ConstrainedSet)
            or is_safe_subclass(field_meta.annotation, ConstrainedList)
            or is_safe_subclass(field_meta.annotation, ConstrainedFrozenSet)
        ):
            result = handle_constrained_collection(
                collection_type=list
                if is_safe_subclass(field_meta.annotation, ConstrainedList)
                else set,  # pyright: ignore
                factory=cls,
                field_meta=field_meta.children[0] if field_meta.children else field_meta,
                item_type=getattr(field_meta.annotation, "item_type", Any),
                max_items=field_meta.annotation.max_items,
                min_items=field_meta.annotation.min_items,
                unique_items=bool(getattr(field_meta.annotation, "unique_items", False)),
            )
            return frozenset(result) if is_safe_subclass(field_meta.annotation, ConstrainedFrozenSet) else result

        if is_safe_subclass(field_meta.annotation, ConstrainedDate):
            return handle_constrained_date(
                faker=cls.__faker__,
                ge=field_meta.annotation.ge,
                gt=field_meta.annotation.gt,
                le=field_meta.annotation.le,
                lt=field_meta.annotation.lt,
            )

        return super().get_field_value(field_meta=field_meta, field_build_parameters=field_build_parameters)

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
