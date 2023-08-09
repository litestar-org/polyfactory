from __future__ import annotations

from contextlib import suppress
from typing import (
    TYPE_CHECKING,
    Any,
    ClassVar,
    ForwardRef,
    Generic,
    Mapping,
    Tuple,
    TypeVar,
    cast,
)

from typing_extensions import Literal, get_args, get_origin

from polyfactory.collection_extender import CollectionExtender
from polyfactory.constants import (
    DEFAULT_RANDOM,
    MAX_COLLECTION_LENGTH,
    MIN_COLLECTION_LENGTH,
    RANDOMIZE_COLLECTION_LENGTH,
)
from polyfactory.exceptions import MissingDependencyException
from polyfactory.factories.base import BaseFactory
from polyfactory.field_meta import Constraints, FieldMeta, Null
from polyfactory.utils.helpers import unwrap_new_type, unwrap_optional
from polyfactory.utils.predicates import is_optional, is_safe_subclass, is_union

try:
    from pydantic import VERSION, BaseModel, Json
    from pydantic.fields import FieldInfo
except ImportError as e:
    raise MissingDependencyException("pydantic is not installed") from e

try:
    from pydantic.fields import ModelField  # type: ignore[attr-defined]
except ImportError:
    ModelField = Any
    from pydantic_core import PydanticUndefined as Undefined

with suppress(ImportError):
    from pydantic_core import to_json

if TYPE_CHECKING:
    from random import Random

    from typing_extensions import NotRequired, TypeGuard

T = TypeVar("T", bound=BaseModel)


class PydanticConstraints(Constraints):
    """Metadata regarding a Pydantic type constraints, if any"""

    json: NotRequired[bool]


class PydanticFieldMeta(FieldMeta):
    """Field meta subclass capable of handling pydantic ModelFields"""

    def __init__(
        self,
        *,
        name: str,
        annotation: type,
        random: Random | None = None,
        default: Any = ...,
        children: list[FieldMeta] | None = None,
        constraints: PydanticConstraints | None = None,
    ) -> None:
        super().__init__(
            name=name, annotation=annotation, random=random, default=default, children=children, constraints=constraints
        )

    @classmethod
    def from_field_info(
        cls,
        field_name: str,
        field_info: FieldInfo,
        use_alias: bool,
        random: Random | None,
        randomize_collection_length: bool = RANDOMIZE_COLLECTION_LENGTH,
        min_collection_length: int = MIN_COLLECTION_LENGTH,
        max_collection_length: int = MAX_COLLECTION_LENGTH,
    ) -> PydanticFieldMeta:
        """Create an instance from a pydantic field info.

        :param field_name: The name of the field.
        :param field_info: A pydantic FieldInfo instance.
        :param use_alias: Whether to use the field alias.
        :param random: A random.Random instance.
        :param randomize_collection_length: Whether to randomize collection length.
        :param min_collection_length: Minimum collection length.
        :param max_collection_length: Maximum collection length.

        :returns: A PydanticFieldMeta instance.
        """
        if callable(field_info.default_factory):
            default_value = field_info.default_factory()
        else:
            default_value = field_info.default if field_info.default is not Undefined else Null

        annotation = unwrap_new_type(field_info.annotation)
        children: list[FieldMeta,] | None = None
        constraints: Constraints = {}
        name = field_info.alias if field_info.alias and use_alias else field_name

        # pydantic v2 does not always propagate metadata for Union types
        if not field_info.metadata and is_optional(annotation):
            field_info = FieldInfo.from_annotation(unwrap_optional(annotation))
        elif is_union(annotation):
            children = [
                cls.from_field_info(
                    field_info=FieldInfo.from_annotation(arg),
                    field_name=field_name,
                    max_collection_length=max_collection_length,
                    min_collection_length=min_collection_length,
                    random=random,
                    randomize_collection_length=randomize_collection_length,
                    use_alias=use_alias,
                )
                for arg in get_args(annotation)
            ]

        metadata, is_json = [], False
        for m in field_info.metadata:
            if not is_json and isinstance(m, Json):  # type: ignore[misc]
                is_json = True
            elif m is not None:
                metadata.append(m)

        constraints = cls.parse_constraints(metadata=metadata) if metadata else {}
        constraints = cast(PydanticConstraints, constraints)

        if "url" in constraints:
            # pydantic uses a sentinel value for url constraints
            annotation = str

        if is_json:
            constraints["json"] = True

        return PydanticFieldMeta.from_type(
            annotation=annotation,
            children=children,
            constraints=cast("Constraints", {k: v for k, v in constraints.items() if v is not None}) or None,
            default=default_value,
            max_collection_length=max_collection_length,
            min_collection_length=min_collection_length,
            name=name,
            random=random or DEFAULT_RANDOM,
            randomize_collection_length=randomize_collection_length,
        )

    @classmethod
    def from_model_field(  # pragma: no cover
        cls,
        model_field: ModelField,  # pyright: ignore
        use_alias: bool,
        randomize_collection_length: bool,
        min_collection_length: int,
        max_collection_length: int,
        random: Random = DEFAULT_RANDOM,
    ) -> PydanticFieldMeta:
        """Create an instance from a pydantic model field.
        :param model_field: A pydantic ModelField.
        :param use_alias: Whether to use the field alias.
        :param randomize_collection_length: A boolean flag whether to randomize collections lengths
        :param min_collection_length: Minimum number of elements in randomized collection
        :param max_collection_length: Maximum number of elements in randomized collection
        :param random: An instance of random.Random.

        :returns: A PydanticFieldMeta instance.

        """
        from pydantic import AmqpDsn, AnyHttpUrl, AnyUrl, HttpUrl, KafkaDsn, PostgresDsn, RedisDsn
        from pydantic.fields import DeferredType, Undefined  # type: ignore

        if model_field.default is not Undefined:
            default_value = model_field.default
        elif callable(model_field.default_factory):
            default_value = model_field.default_factory()
        else:
            default_value = model_field.default if model_field.default is not Undefined else Null

        name = model_field.alias if model_field.alias and use_alias else model_field.name

        outer_type = unwrap_new_type(model_field.outer_type_)
        annotation = (
            model_field.outer_type_
            if isinstance(model_field.annotation, (DeferredType, ForwardRef))
            else unwrap_new_type(model_field.annotation)
        )

        constraints = cast(
            "Constraints",
            {
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
        if unwrap_optional(annotation) in (
            AnyUrl,
            HttpUrl,
            KafkaDsn,
            PostgresDsn,
            RedisDsn,
            AmqpDsn,
            AnyHttpUrl,
        ):
            constraints = {}

        if model_field.field_info.const and (
            default_value is None or isinstance(default_value, (int, bool, str, bytes))
        ):
            annotation = Literal[default_value]  # pyright: ignore

        children: list[FieldMeta] = []
        if model_field.key_field or model_field.sub_fields:
            number_of_args = (
                random.randint(min_collection_length, max_collection_length) if randomize_collection_length else 1
            )
            fields_to_iterate = (
                ([model_field.key_field, *model_field.sub_fields])
                if model_field.key_field is not None
                else model_field.sub_fields
            )
            type_args = tuple(
                (
                    sub_field.outer_type_
                    if isinstance(sub_field.annotation, DeferredType)
                    else unwrap_new_type(sub_field.annotation)
                )
                for sub_field in fields_to_iterate
            )
            type_arg_to_sub_field = dict(zip(type_args, fields_to_iterate))
            if get_origin(outer_type) in (tuple, Tuple) and get_args(outer_type)[-1] == Ellipsis:
                # pydantic removes ellipses from Tuples in sub_fields
                type_args += (...,)
            extended_type_args = CollectionExtender.extend_type_args(annotation, type_args, number_of_args)
            children.extend(
                PydanticFieldMeta.from_model_field(
                    model_field=type_arg_to_sub_field[arg],
                    use_alias=use_alias,
                    random=random,
                    randomize_collection_length=randomize_collection_length,
                    min_collection_length=min_collection_length,
                    max_collection_length=max_collection_length,
                )
                for arg in extended_type_args
            )

        return PydanticFieldMeta(
            name=name,
            random=random or DEFAULT_RANDOM,
            annotation=annotation,
            children=children or None,
            default=default_value,
            constraints=cast("PydanticConstraints", {k: v for k, v in constraints.items() if v is not None}) or None,
        )


class ModelFactory(Generic[T], BaseFactory[T]):
    """Base factory for pydantic models"""

    __forward_ref_resolution_type_mapping__: ClassVar[Mapping[str, type]] = {}
    __is_base_factory__ = True

    def __init_subclass__(cls, *args: Any, **kwargs: Any) -> None:
        super().__init_subclass__(*args, **kwargs)

        if (
            VERSION.startswith("1")
            and getattr(cls, "__model__", None)
            and hasattr(cls.__model__, "update_forward_refs")
        ):
            with suppress(NameError):  # pragma: no cover
                cls.__model__.update_forward_refs(**cls.__forward_ref_resolution_type_mapping__)

    @classmethod
    def is_supported_type(cls, value: Any) -> TypeGuard[type[T]]:
        """Determine whether the given value is supported by the factory.

        :param value: An arbitrary value.
        :returns: A typeguard
        """
        return is_safe_subclass(value, BaseModel)

    @classmethod
    def get_model_fields(cls) -> list["FieldMeta"]:
        """Retrieve a list of fields from the factory's model.


        :returns: A list of field MetaData instances.

        """
        if "_fields_metadata" not in cls.__dict__:
            if VERSION.startswith("1"):
                cls._fields_metadata = [
                    PydanticFieldMeta.from_model_field(
                        field,
                        use_alias=not cls.__model__.__config__.allow_population_by_field_name,  # type: ignore[attr-defined]
                        random=cls.__random__,
                        randomize_collection_length=cls.__randomize_collection_length__,
                        min_collection_length=cls.__min_collection_length__,
                        max_collection_length=cls.__max_collection_length__,
                    )
                    for field in cls.__model__.__fields__.values()  # type: ignore[attr-defined]
                ]
            else:
                cls._fields_metadata = [
                    PydanticFieldMeta.from_field_info(
                        field_info=field_info,
                        field_name=field_name,
                        random=cls.__random__,
                        use_alias=not cls.__model__.model_config.get("populate_by_name", False),
                        randomize_collection_length=cls.__randomize_collection_length__,
                        min_collection_length=cls.__min_collection_length__,
                        max_collection_length=cls.__max_collection_length__,
                    )
                    for field_name, field_info in cls.__model__.model_fields.items()
                ]
        return cls._fields_metadata

    @classmethod
    def get_constrained_field_value(cls, annotation: Any, field_meta: FieldMeta) -> Any:
        constraints = cast(PydanticConstraints, field_meta.constraints)
        if constraints.pop("json", None):
            value = cls.get_field_value(field_meta)
            return to_json(value)

        return super().get_constrained_field_value(annotation, field_meta)

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
