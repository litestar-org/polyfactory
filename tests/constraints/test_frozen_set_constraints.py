from contextlib import suppress
from typing import Any, Optional

import pytest
from hypothesis import given
from hypothesis.strategies import integers
from pydantic import BaseConfig, ConstrainedFrozenSet
from pydantic.fields import ModelField

from pydantic_factories import ModelFactory
from pydantic_factories.constraints.collection import handle_constrained_collection
from pydantic_factories.exceptions import ParameterError


def create_model_field(
    item_type: Any,
    min_items: Optional[int] = None,
    max_items: Optional[int] = None,
) -> ModelField:
    field = ConstrainedFrozenSet()
    field.min_items = min_items
    field.max_items = max_items
    field.item_type = item_type
    model_field = ModelField(name="", class_validators={}, model_config=BaseConfig, type_=item_type)
    model_field.outer_type_ = field
    return model_field


@given(
    integers(min_value=0, max_value=10),
    integers(min_value=0, max_value=10),
)
def test_handle_constrained_set_with_min_items_and_max_items(min_items: int, max_items: int) -> None:
    if max_items >= min_items:
        field = create_model_field(str, min_items=min_items, max_items=max_items)
        result = handle_constrained_collection(collection_type=set, model_field=field, model_factory=ModelFactory)
        assert len(result) >= min_items
        assert len(result) <= max_items
    else:
        field = create_model_field(str, min_items=min_items, max_items=max_items)
        with pytest.raises(ParameterError):
            handle_constrained_collection(collection_type=set, model_field=field, model_factory=ModelFactory)


@given(
    integers(min_value=0, max_value=10),
)
def test_handle_constrained_set_with_max_items(
    max_items: int,
) -> None:
    field = create_model_field(str, max_items=max_items)
    result = handle_constrained_collection(collection_type=set, model_field=field, model_factory=ModelFactory)
    assert len(result) <= max_items


@given(
    integers(min_value=0, max_value=10),
)
def test_handle_constrained_set_with_min_items(
    min_items: int,
) -> None:
    field = create_model_field(str, min_items=min_items)
    result = handle_constrained_collection(collection_type=set, model_field=field, model_factory=ModelFactory)
    assert len(result) >= min_items


def test_handle_constrained_set_with_different_types() -> None:
    with suppress(ParameterError):
        for t_type in ModelFactory.get_provider_map():
            field = create_model_field(t_type, min_items=1)
            result = handle_constrained_collection(collection_type=set, model_field=field, model_factory=ModelFactory)
            assert len(result) > 0
