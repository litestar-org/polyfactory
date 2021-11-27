from collections import defaultdict, deque
from dataclasses import is_dataclass
from random import choice
from typing import TYPE_CHECKING, Any, Callable, Optional, Type, cast

from pydantic.fields import (
    SHAPE_DEFAULTDICT,
    SHAPE_DEQUE,
    SHAPE_DICT,
    SHAPE_FROZENSET,
    SHAPE_ITERABLE,
    SHAPE_LIST,
    SHAPE_MAPPING,
    SHAPE_SEQUENCE,
    SHAPE_SET,
    SHAPE_TUPLE,
    SHAPE_TUPLE_ELLIPSIS,
    ModelField,
)

from pydantic_factories.exceptions import ParameterError
from pydantic_factories.utils import is_any, is_optional, is_pydantic_model, is_union
from pydantic_factories.value_generators.primitives import (
    create_random_boolean,
    create_random_string,
)

if TYPE_CHECKING:  # pragma: no cover
    from pydantic_factories.factory import ModelFactory

type_mapping = {
    "Dict": dict,
    "Sequence": list,
    "List": list,
    "Set": set,
    "Deque": deque,
    "Mapping": dict,
    "Tuple": tuple,
    "DefaultDict": defaultdict,
    "FrozenSet": frozenset,
    "Iterable": list,
}

shape_mapping = {
    SHAPE_LIST: list,
    SHAPE_SET: set,
    SHAPE_MAPPING: dict,
    SHAPE_TUPLE: tuple,
    SHAPE_TUPLE_ELLIPSIS: tuple,
    SHAPE_SEQUENCE: list,
    SHAPE_FROZENSET: frozenset,
    SHAPE_ITERABLE: list,
    SHAPE_DEQUE: deque,
    SHAPE_DICT: dict,
    SHAPE_DEFAULTDICT: defaultdict,
}


def handle_container_type(model_field: ModelField, container_type: Callable, model_factory: Type["ModelFactory"]):
    """Handles generation of container types, e.g. dict, list etc. recursively"""
    is_frozen_set = False
    if container_type == frozenset:
        container = set()
        is_frozen_set = True
    else:
        container = container_type()
    value = None
    if model_field.sub_fields:
        value = handle_complex_type(model_field=choice(model_field.sub_fields), model_factory=model_factory)
    if value is not None:
        if isinstance(container, (dict, defaultdict)):
            container[handle_complex_type(model_field=model_field.key_field, model_factory=model_factory)] = value
        elif isinstance(container, (list, deque)):
            container.append(value)
        else:
            container.add(value)
            if is_frozen_set:
                container = cast(set, frozenset(*container))
    return container


def handle_complex_type(model_field: ModelField, model_factory: Type["ModelFactory"]) -> Any:
    """Recursive type generation based on typing info stored in the graph like structure of pydantic model_fields"""

    providers = model_factory.get_provider_map()
    field_type = model_field.type_
    container_type: Optional[Callable] = shape_mapping.get(model_field.shape)
    if container_type:
        if container_type != tuple:
            return handle_container_type(
                model_field=model_field, container_type=container_type, model_factory=model_factory
            )
        return tuple(
            handle_complex_type(model_field=sub_field, model_factory=model_factory)
            for sub_field in (model_field.sub_fields or [])
        )
    if is_union(model_field=model_field) and model_field.sub_fields:
        return handle_complex_type(model_field=choice(model_field.sub_fields), model_factory=model_factory)
    if is_any(model_field=model_field):
        return create_random_string(min_length=1, max_length=10)
    if is_optional(model_field) and not create_random_boolean():
        return None
    if field_type in model_factory.get_provider_map():
        return providers[field_type]()
    if is_pydantic_model(field_type) or is_dataclass(field_type):
        return model_factory.create_factory(model=field_type).build()
    if model_factory.is_ignored_type(field_type):
        return None
    raise ParameterError(
        f"Unsupported type: {repr(field_type)}"
        f"\n\nEither extend the providers map or add a factory function for this model field"
    )
