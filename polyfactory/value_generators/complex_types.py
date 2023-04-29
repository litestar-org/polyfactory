from __future__ import annotations

from typing import TYPE_CHECKING, AbstractSet, Any, MutableMapping, MutableSequence, Set, TypeVar

from typing_extensions import is_typeddict

from polyfactory.field_meta import FieldMeta
from polyfactory.utils.helpers import unwrap_annotation, unwrap_args
from polyfactory.utils.predicates import get_type_origin, is_any, is_union
from polyfactory.value_generators.primitives import create_random_string

if TYPE_CHECKING:
    from polyfactory.factories.base import BaseFactory


def handle_collection_type(field_meta: FieldMeta, container_type: type, factory: type[BaseFactory]) -> Any:
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
        key_type, value_type = unwrap_args(field_meta.annotation) or (str, str)
        key = handle_complex_type(FieldMeta.from_type(key_type), factory)
        if is_union(value_type) and field_meta.children:
            value_field_meta = factory.__random__.choice(field_meta.children)
            value = handle_complex_type(value_field_meta, factory)
        else:
            value = handle_complex_type(FieldMeta.from_type(value_type), factory)
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


def handle_complex_type(field_meta: FieldMeta, factory: type[BaseFactory]) -> Any:
    """Recursive type generation based on typing info stored in the graph like structure
    of pydantic field_metas.

    :param field_meta: A field meta instance.
    :param factory: A factory.

    :returns: A built result.
    """
    if origin := get_type_origin(unwrap_annotation(field_meta.annotation)):
        return handle_collection_type(field_meta, origin, factory)

    if is_union(field_meta.annotation) and field_meta.children:
        return handle_complex_type(factory.__random__.choice(field_meta.children), factory)

    if is_any(field_meta.annotation) or isinstance(field_meta.annotation, TypeVar):
        return create_random_string(factory.__random__, min_length=1, max_length=10)

    return factory.get_field_value(field_meta)
