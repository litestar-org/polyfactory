from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable, TypeVar

from polyfactory.exceptions import ParameterException

if TYPE_CHECKING:
    from polyfactory.factories.base import BaseFactory
    from polyfactory.field_meta import FieldMeta

T = TypeVar("T", list, set, frozenset)


def handle_constrained_collection(
    collection_type: Callable[..., T],
    factory: type[BaseFactory[Any]],
    field_meta: FieldMeta,
    item_type: Any,
    max_items: int | None = None,
    min_items: int | None = None,
    unique_items: bool = False,
) -> T:
    """Generate a constrained list or set.

    :param collection_type: A type that can accept type arguments.
    :param factory: A factory.
    :param field_meta: A field meta instance.
    :param item_type: Type of the collection items.
    :param max_items: Maximal number of items.
    :param min_items: Minimal number of items.
    :param unique_items: Whether the items should be unique.

    :returns: A collection value.
    """
    min_items = abs(min_items if min_items is not None else (max_items or 0))
    max_items = abs(max_items if max_items is not None else min_items + 1)

    if max_items < min_items:
        raise ParameterException("max_items must be larger or equal to min_items")

    collection: set[T] | list[T] = set() if (collection_type in (frozenset, set) or unique_items) else []

    try:
        length = factory.__random__.randint(min_items, max_items) or 1
        while len(collection) < length:
            value = factory.get_field_value(field_meta)
            if isinstance(collection, set):
                collection.add(value)
            else:
                collection.append(value)
        return collection_type(collection)
    except TypeError as e:
        raise ParameterException(f"cannot generate a constrained collection of type: {item_type}") from e
