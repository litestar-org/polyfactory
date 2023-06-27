from contextlib import suppress
from random import Random
from typing import Any

import pytest
from hypothesis import given
from hypothesis.strategies import integers

from polyfactory.exceptions import ParameterException
from polyfactory.factories.pydantic_factory import ModelFactory
from polyfactory.field_meta import FieldMeta
from polyfactory.value_generators.constrained_collections import (
    handle_constrained_collection,
)


@given(
    integers(min_value=0, max_value=10),
    integers(min_value=0, max_value=10),
)
def test_handle_constrained_set_with_min_items_and_max_items(min_items: int, max_items: int) -> None:
    if max_items >= min_items:
        result = handle_constrained_collection(
            collection_type=frozenset,
            factory=ModelFactory,
            field_meta=FieldMeta(name="test", annotation=frozenset, random=Random()),
            item_type=str,
            max_items=max_items,
            min_items=min_items,
        )
        assert len(result) >= min_items
        assert len(result) <= max_items or 1
    else:
        with pytest.raises(ParameterException):
            handle_constrained_collection(
                collection_type=frozenset,
                factory=ModelFactory,
                field_meta=FieldMeta(name="test", annotation=frozenset, random=Random()),
                item_type=str,
                max_items=max_items,
                min_items=min_items,
            )


@given(
    integers(min_value=0, max_value=10),
)
def test_handle_constrained_set_with_max_items(
    max_items: int,
) -> None:
    result = handle_constrained_collection(
        collection_type=frozenset,
        factory=ModelFactory,
        field_meta=FieldMeta(name="test", annotation=frozenset, random=Random()),
        item_type=str,
        max_items=max_items,
    )
    assert len(result) <= max_items or 1


@given(
    integers(min_value=0, max_value=10),
)
def test_handle_constrained_set_with_min_items(
    min_items: int,
) -> None:
    result = handle_constrained_collection(
        collection_type=frozenset,
        factory=ModelFactory,
        field_meta=FieldMeta(name="test", annotation=frozenset, random=Random()),
        item_type=str,
        min_items=min_items,
    )
    assert len(result) >= min_items


@pytest.mark.parametrize("t_type", tuple(ModelFactory.get_provider_map()))
def test_handle_constrained_set_with_different_types(t_type: Any) -> None:
    with suppress(ParameterException):
        result = handle_constrained_collection(
            collection_type=frozenset,
            factory=ModelFactory,
            field_meta=FieldMeta(name="test", annotation=frozenset, random=Random()),
            item_type=t_type,
        )
        assert len(result) > 0
