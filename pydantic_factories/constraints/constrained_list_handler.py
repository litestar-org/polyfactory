from typing import Any, Callable, Dict, List, cast

from pydantic import ConstrainedList

from pydantic_factories.value_generators.constrained_collection import (
    generate_constrained_collection,
)


def handle_constrained_list(field: ConstrainedList, providers: Dict[Any, Callable]) -> List[Any]:
    """Handle ConstrainedList instances"""
    return cast(
        List,
        generate_constrained_collection(
            t_type=field.item_type,
            collection_type=list,
            min_items=field.min_items,
            max_items=field.max_items,
            providers=providers,
        ),
    )
