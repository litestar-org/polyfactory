from typing import Any, Callable, Dict, Set, cast

from pydantic import ConstrainedSet

from pydantic_factories.exceptions import ParameterError
from pydantic_factories.value_generators.constrained_collection import (
    generate_constrained_collection,
)


def handle_constrained_set(field: ConstrainedSet, providers: Dict[Any, Callable]) -> Set[Any]:
    """Handle ConstrainedSet instances"""
    try:
        return cast(
            Set,
            generate_constrained_collection(
                t_type=field.item_type,
                collection_type=set,
                min_items=field.min_items,
                max_items=field.max_items,
                providers=providers,
            ),
        )
    except TypeError as e:
        raise ParameterError(f"cannot generate a constrained set of an hashable type: {field.item_type}") from e
