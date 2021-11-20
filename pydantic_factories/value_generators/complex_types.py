from collections import deque, defaultdict
from random import choice
from typing import (
    Any,
    Optional,
    Callable,
)

from pydantic.fields import (
    ModelField,
    # SHAPE_SINGLETON,
    SHAPE_LIST,
    SHAPE_SET,
    SHAPE_MAPPING,
    SHAPE_TUPLE,
    SHAPE_TUPLE_ELLIPSIS,
    SHAPE_SEQUENCE,
    SHAPE_FROZENSET,
    SHAPE_ITERABLE,
    # SHAPE_GENERIC,
    SHAPE_DEQUE,
    SHAPE_DICT,
    SHAPE_DEFAULTDICT,
    SHAPE_GENERIC,
)

from pydantic_factories.exceptions import ParameterError
from pydantic_factories.value_generators.primitives import create_random_string

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
    # SHAPE_SINGLETON: dict,  # fixme
    SHAPE_LIST: list,
    SHAPE_SET: set,
    SHAPE_MAPPING: dict,
    SHAPE_TUPLE: tuple,
    SHAPE_TUPLE_ELLIPSIS: tuple,
    SHAPE_SEQUENCE: list,
    SHAPE_FROZENSET: frozenset,
    SHAPE_ITERABLE: list,
    # SHAPE_GENERIC: dict,  # fixme
    SHAPE_DEQUE: deque,
    SHAPE_DICT: dict,
    SHAPE_DEFAULTDICT: defaultdict,
}


def validate_is_not_generic(shape: int):
    """validates that the field's shapre is not generic"""
    if shape == SHAPE_GENERIC:
        raise ParameterError("Generic typings are not supported")


def is_union(model_field: ModelField) -> bool:
    return "typing.Union" == repr(model_field.outer_type_).split("[")[0]


def is_any(model_field: ModelField) -> bool:
    try:
        name = getattr(model_field.outer_type_, "_name")
        return name and "Any" in name
    except AttributeError:
        return False


def handle_container_type(model_field: ModelField, container_type: Callable, providers: dict[Any, Callable]):
    is_frozen_set = False
    is_tuple = False
    if container_type == frozenset:
        container = set()
        is_frozen_set = True
    elif container_type == tuple:
        container = list()
        is_tuple = True
    else:
        container = container_type()
    try:
        if model_field.sub_fields:
            value = handle_complex_type(model_field=choice(model_field.sub_fields), providers=providers)
        elif model_field.type_ != Any:
            handler = providers[model_field.type_]
            value = handler()
        else:
            value = create_random_string(min_length=1, max_length=10)
        if isinstance(container, (dict, defaultdict)):
            container[handle_complex_type(model_field=model_field.key_field, providers=providers)] = value
        elif isinstance(container, (list, deque)):
            container.append(value)
            if is_tuple:
                container = tuple(*container)
        else:
            container.add(value)
            if is_frozen_set:
                container = frozenset(*container)
        return container
    except KeyError:
        raise ParameterError("Unsupported type")


def handle_complex_type(model_field: ModelField, providers: dict[Any, Callable]) -> Any:
    validate_is_not_generic(shape=model_field.shape)
    container_type: Optional[Callable] = shape_mapping.get(model_field.shape)
    if container_type:
        return handle_container_type(model_field=model_field, container_type=container_type, providers=providers)
    else:
        if is_union(model_field=model_field):
            return handle_complex_type(model_field=choice(model_field.sub_fields), providers=providers)
        if is_any(model_field=model_field):
            return create_random_string(min_length=1, max_length=10)
        if model_field.type_ in providers.keys():
            return providers[model_field.type_]()
        raise ParameterError(
            f"Unsupported type: {repr(model_field.type_)}"
            f"\n\nEither extend the providers map or add a factory function for this model field"
        )
