from __future__ import annotations

from typing import TYPE_CHECKING, AbstractSet, Any, MutableMapping, MutableSequence, Set

from typing_extensions import is_typeddict

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
        key = factory.get_field_value(field_meta.children[0])
        value = factory.get_field_value(field_meta.children[1])
        container[key] = value

    elif issubclass(container_type, MutableSequence):
        container.append(factory.get_field_value(field_meta.children[0]))

    elif issubclass(container_type, Set):
        container.add(factory.get_field_value(field_meta.children[0]))

    elif issubclass(container_type, AbstractSet):
        container = container.union(handle_collection_type(field_meta, set, factory))

    elif issubclass(container_type, tuple):
        container = container_type(map(factory.get_field_value, field_meta.children))

    else:
        raise NotImplementedError(f"Unsupported container type: {container_type}")

    return container
