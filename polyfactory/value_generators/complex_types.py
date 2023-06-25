from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    AbstractSet,
    Any,
    Collection,
    MutableMapping,
    MutableSequence,
    Set,
    TypeVar,
)

from typing_extensions import get_args, is_typeddict

from polyfactory.utils.helpers import unwrap_annotation
from polyfactory.utils.predicates import get_type_origin, is_any, is_literal, is_union
from polyfactory.value_generators.primitives import create_random_string

if TYPE_CHECKING:
    from polyfactory.factories.base import BaseFactory
    from polyfactory.field_meta import FieldMeta


def handle_collection_type(field_meta: FieldMeta, container_type: type, factory: type[BaseFactory[Any]]) -> Any:
    """Handle generation of container types recursively.

    :param container_type: A type that can accept type arguments.
    :param factory: A factory.
    :param field_meta: A field meta instance.

    :returns: A built result.
    """
    container = container_type()
    if not field_meta.children:
        return container

    if issubclass(container_type, MutableMapping) or is_typeddict(container_type):
        key = handle_complex_type(field_meta.children[0], factory)
        value = handle_complex_type(field_meta.children[1], factory)
        container[key] = value

    elif issubclass(container_type, MutableSequence):
        container.append(handle_complex_type(field_meta.children[0], factory))

    elif issubclass(container_type, Set):
        container.add(handle_complex_type(field_meta.children[0], factory))

    elif issubclass(container_type, AbstractSet):
        container = container.union(handle_collection_type(field_meta, set, factory))

    elif issubclass(container_type, tuple):
        container = container_type(handle_complex_type(subfield_meta, factory) for subfield_meta in field_meta.children)

    else:
        raise NotImplementedError(f"Unsupported container type: {container_type}")

    return container


def handle_complex_type(field_meta: FieldMeta, factory: type[BaseFactory[Any]]) -> Any:
    """Recursive type generation based on typing info stored in the graph like structure
    of pydantic field_metas.

    :param field_meta: A field meta instance.
    :param factory: A factory.

    :returns: A built result.
    """
    unwrapped_annotation = unwrap_annotation(field_meta.annotation, random=factory.__random__)

    if is_literal(annotation=unwrapped_annotation) and (literal_args := get_args(unwrapped_annotation)):
        return factory.__random__.choice(literal_args)

    if origin := get_type_origin(unwrapped_annotation):
        if issubclass(origin, Collection):
            return handle_collection_type(field_meta, origin, factory)
        return factory.get_mock_value(origin)

    if is_union(field_meta.annotation) and field_meta.children:
        return factory.get_field_value(factory.__random__.choice(field_meta.children))

    if is_any(field_meta.annotation) or isinstance(field_meta.annotation, TypeVar):
        return create_random_string(factory.__random__, min_length=1, max_length=10)

    return factory.get_field_value(field_meta)
