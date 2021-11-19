from contextlib import suppress
from typing import Any, Optional

import pytest
from hypothesis import given
from hypothesis.strategies import integers
from pydantic import ConstrainedSet

from pydantic_factories import ModelFactory
from pydantic_factories.constraints.constrained_set_handler import (
    handle_constrained_set,
)
from pydantic_factories.exceptions import ParameterError


def create_constrained_field(
    item_type: Any,
    min_items: Optional[int] = None,
    max_items: Optional[int] = None,
) -> ConstrainedSet:
    field = ConstrainedSet()
    field.min_items = min_items
    field.max_items = max_items
    field.item_type = item_type
    return field


@given(
    integers(min_value=0, max_value=10),
    integers(min_value=0, max_value=10),
)
def test_handle_constrained_set_with_min_items_and_max_items(min_items: int, max_items: int):
    if max_items >= min_items:
        field = create_constrained_field(str, min_items=min_items, max_items=max_items)
        result = handle_constrained_set(field, ModelFactory.get_provider_map())
        assert len(result) >= min_items
        assert len(result) <= max_items
    else:
        with pytest.raises(AssertionError):
            handle_constrained_set(
                create_constrained_field(str, min_items=min_items, max_items=max_items), ModelFactory.get_provider_map()
            )


@given(
    integers(min_value=0, max_value=10),
)
def test_handle_constrained_set_with_max_items(
    max_items: int,
):
    field = create_constrained_field(str, max_items=max_items)
    result = handle_constrained_set(field, ModelFactory.get_provider_map())
    assert len(result) <= max_items


@given(
    integers(min_value=0, max_value=10),
)
def test_handle_constrained_set_with_min_items(
    min_items: int,
):
    field = create_constrained_field(str, min_items=min_items)
    result = handle_constrained_set(field, ModelFactory.get_provider_map())
    assert len(result) >= min_items


def test_handle_constrained_set_with_different_types():
    with suppress(ParameterError):
        for t_type in ModelFactory.get_provider_map().keys():
            field = create_constrained_field(t_type, min_items=1)
            result = handle_constrained_set(field, ModelFactory.get_provider_map())
            assert len(result) > 0
