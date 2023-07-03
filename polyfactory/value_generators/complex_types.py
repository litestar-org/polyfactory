from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    AbstractSet,
    Any,
    Iterable,
    MutableMapping,
    MutableSequence,
    Set,
    Tuple,
    cast,
)

from typing_extensions import is_typeddict

from polyfactory.field_meta import FieldMeta

if TYPE_CHECKING:
    from polyfactory.factories.base import BaseFactory


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
        for key_field_meta, value_field_meta in cast(
            Iterable[Tuple[FieldMeta, FieldMeta]], zip(field_meta.children[::2], field_meta.children[1::2])
        ):
            key = factory.get_field_value(key_field_meta)
            value = factory.get_field_value(value_field_meta)
            container[key] = value
        return container

    if issubclass(container_type, MutableSequence):
        for subfield_meta in field_meta.children:
            container.append(factory.get_field_value(subfield_meta))
        return container

    if issubclass(container_type, Set):
        for subfield_meta in field_meta.children:
            container.add(factory.get_field_value(subfield_meta))
        return container

    if issubclass(container_type, AbstractSet):
        return container.union(handle_collection_type(field_meta, set, factory))

    if issubclass(container_type, tuple):
        return container_type(map(factory.get_field_value, field_meta.children))

    raise NotImplementedError(f"Unsupported container type: {container_type}")
