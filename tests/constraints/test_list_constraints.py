from typing import Any, Optional

from pydantic import ConstrainedList

from pydantic_factories.constraints.objects import handle_constrained_list


def create_constrained_field(
    item_type: Any,
    min_items: Optional[int] = None,
    max_items: Optional[int] = None,
) -> ConstrainedList:
    field = ConstrainedList()
    field.min_items = min_items
    field.max_items = max_items
    field.item_type = item_type
    return field


def test_handle_constrained_list_with_min_items_and_max_items():
    field = create_constrained_field(str)
    assert handle_constrained_list(field) == []
