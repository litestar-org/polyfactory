from random import randint
from typing import Any, Callable, Dict, Optional, Union

from typing_extensions import Type

from pydantic_factories.exceptions import ParameterError


def generate_constrained_collection(
    t_type: Any,
    collection_type: Union[Type[list], Type[set]],
    providers: Dict[Any, Callable],
    min_items: Optional[int] = None,
    max_items: Optional[int] = None,
) -> Union[list, set]:
    """Generate a constrained list or set"""
    if min_items is None:
        min_items = 0
    if max_items is None:
        max_items = min_items + 1
    assert max_items >= min_items, "max_items must be longer or equal to min_items"
    if t_type is Any:
        t_type = str
    collection: Union[list, set] = collection_type()
    handler = providers.get(t_type)
    if not handler:
        raise ParameterError(f"cannot generate a constrained {t_type.__name__} of ${t_type.__name__} elements")
    while len(collection) < randint(min_items, max_items):
        value = handler()
        if isinstance(collection, set):
            collection.add(value)
        else:
            collection.append(value)
    return collection
