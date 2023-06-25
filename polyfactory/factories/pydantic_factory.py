from __future__ import annotations

from contextlib import suppress
from inspect import isclass
from typing import (
    TYPE_CHECKING,
    Any,
    ClassVar,
    Generic,
    Literal,
    Mapping,
    TypeVar,
    cast,
)

from polyfactory.exceptions import MissingDependencyException
from polyfactory.factories.base import BaseFactory
from polyfactory.field_meta import Constraints, FieldMeta, Null
from polyfactory.utils.helpers import unwrap_new_type, unwrap_optional
from polyfactory.utils.predicates import is_optional_union

try:
    from pydantic import BaseModel

except ImportError as e:
    raise MissingDependencyException("pydantic is not installed") from e

try:
    from pydantic.fields import ModelField  # type: ignore[attr-defined]

    pydantic_version: Literal[1, 2] = 1
except ImportError:
    pydantic_version = 2

    ModelField = Any
    from pydantic._internal._fields import Undefined

if TYPE_CHECKING:
    from random import Random

    from pydantic.fields import FieldInfo
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

    # FIXME: remove the pragma when switching to pydantic v2 permanently
    @classmethod
    def from_field_info(
        cls, field_name: str, field_info: FieldInfo, use_alias: bool, random: Random
    ) -> PydanticFieldMeta:  # pragma: no cover
        """Create an instance from a pydantic field info.

        :param field_name: The name of the field.
        :param field_info: A pydantic FieldInfo instance.
        :param use_alias: Whether to use the field alias.
        :param random: A random.Random instance.

        :returns: A PydanticFieldMeta instance.
        """
        if callable(field_info.default_factory):
            default_value = field_info.default_factory()
        else:
            default_value = field_info.default if field_info.default is not Undefined else Null

        name = field_info.alias if field_info.alias and use_alias else field_name

        annotation = unwrap_new_type(field_info.annotation)

        if is_optional_union(field_info.annotation):
            # pydantic v2 do not propagate metadata for Union types #[?]
            # hence we cannot acquire any constraints w/ straightforward approach
            from pydantic.fields import FieldInfo

            field_info = FieldInfo.from_annotation(unwrap_optional(annotation))

        if metadata := [v for v in field_info.metadata if v is not None]:
            constraints = cls.parse_constraints(metadata=metadata)
        else:
            constraints = {}

        if "url" in constraints:
            # pydantic uses a sentinel value for url constraints
            annotation = str

        return PydanticFieldMeta.from_type(
            name=name,
            random=random,
            annotation=annotation,
            default=default_value,
            constraints=cast("Constraints", {k: v for k, v in constraints.items() if v is not None}) or None,
        )

    @classmethod
    def from_model_field(cls, model_field: ModelField, use_alias: bool) -> PydanticFieldMeta:  # pyright: ignore
        """Create an instance from a pydantic model field.

        :param model_field: A pydantic ModelField.
        :param use_alias: Whether to use the field alias.

        :returns: A PydanticFieldMeta instance.

        """
        from pydantic import AmqpDsn, AnyHttpUrl, AnyUrl, HttpUrl, KafkaDsn, PostgresDsn, RedisDsn
        from pydantic.fields import DeferredType, Undefined  # type: ignore

        if callable(model_field.default_factory):
            default_value = model_field.default_factory()
        else:
            default_value = model_field.default if model_field.default is not Undefined else Null

        name = model_field.alias if model_field.alias and use_alias else model_field.name

        outer_type = unwrap_new_type(model_field.outer_type_)
        annotation = (
            unwrap_new_type(model_field.annotation)
            if not isinstance(model_field.annotation, DeferredType)
            else model_field.outer_type_
        )

        constraints = cast(
            "Constraints",
            {
                "constant": bool(model_field.field_info.const) or None,
                "ge": getattr(outer_type, "ge", model_field.field_info.ge),
                "gt": getattr(outer_type, "gt", model_field.field_info.gt),
                "le": getattr(outer_type, "le", model_field.field_info.le),
                "lt": getattr(outer_type, "lt", model_field.field_info.lt),
                "min_length": (
                    getattr(outer_type, "min_length", model_field.field_info.min_length)
                    or getattr(outer_type, "min_items", model_field.field_info.min_items)
                ),
                "max_length": (
                    getattr(outer_type, "max_length", model_field.field_info.max_length)
                    or getattr(outer_type, "max_items", model_field.field_info.max_items)
                ),
                "pattern": getattr(outer_type, "regex", model_field.field_info.regex),
                "unique_items": getattr(outer_type, "unique_items", model_field.field_info.unique_items),
                "decimal_places": getattr(outer_type, "decimal_places", None),
                "max_digits": getattr(outer_type, "max_digits", None),
                "multiple_of": getattr(outer_type, "multiple_of", None),
                "upper_case": getattr(outer_type, "to_upper", None),
                "lower_case": getattr(outer_type, "to_lower", None),
                "item_type": getattr(outer_type, "item_type", None),
            },
        )

        # pydantic v1 has constraints set for these values, but we generate them using faker
        if pydantic_version == 1 and unwrap_optional(annotation) in (
            AnyUrl,
            HttpUrl,
            KafkaDsn,
            PostgresDsn,
            RedisDsn,
            AmqpDsn,
            AnyHttpUrl,
        ):
            constraints = {}

        children: list[FieldMeta] = []
        if model_field.key_field:
            children.append(PydanticFieldMeta.from_model_field(model_field.key_field, use_alias))
        if model_field.sub_fields:
            children.extend(
                PydanticFieldMeta.from_model_field(sub_field, use_alias) for sub_field in model_field.sub_fields
            )

        return PydanticFieldMeta(
            name=name,
            random=cls.random,
            annotation=annotation,
            children=children,
            default=default_value,
            constraints=cast("Constraints", {k: v for k, v in constraints.items() if v is not None}) or None,
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
    def get_model_fields(cls) -> list["FieldMeta"]:
        """Retrieve a list of fields from the factory's model.


        :returns: A list of field MetaData instances.

        """
        if "_fields_metadata" not in cls.__dict__:
            if pydantic_version == 1:
                cls._fields_metadata = [
                    PydanticFieldMeta.from_model_field(
                        field,
                        use_alias=not cls.__model__.__config__.allow_population_by_field_name,
                    )
                    for field in cls.__model__.__fields__.values()  # type: ignore[attr-defined]
                ]
            # FIXME: remove the pragma when switching to pydantic v2 permanently
            else:  # pragma: no cover
                cls._fields_metadata = [
                    PydanticFieldMeta.from_field_info(
                        field_info=field_info,
                        field_name=field_name,
                        random=cls.__random__,
                        use_alias=not cls.__model__.model_config.get("populate_by_name", False),
                    )
                    for field_name, field_info in cls.__model__.model_fields.items()
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
            return (
                cls.__model__.model_construct(**processed_kwargs)
                if hasattr(cls.__model__, "model_construct")
                else cls.__model__.construct(**processed_kwargs)
            )

        return cls.__model__(**processed_kwargs)

    @classmethod
    def is_custom_root_field(cls, field_meta: FieldMeta) -> bool:
        """Determine whether the field is a custom root field.

        :param field_meta: FieldMeta instance.

        :returns: A boolean determining whether the field is a custom root.

        """
        return field_meta.name == "__root__"

    @classmethod
    def should_set_field_value(cls, field_meta: FieldMeta, **kwargs: Any) -> bool:
        """Determine whether to set a value for a given field_name.
        This is an override of BaseFactory.should_set_field_value.

        :param field_meta: FieldMeta instance.
        :param kwargs: Any kwargs passed to the factory.

        :returns: A boolean determining whether a value should be set for the given field_meta.

        """
        return field_meta.name not in kwargs and (
            not field_meta.name.startswith("_") or cls.is_custom_root_field(field_meta)
        )
