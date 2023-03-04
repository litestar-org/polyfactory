from contextlib import suppress
from typing import TYPE_CHECKING, Any, Optional

import pytest
from hypothesis import given
from hypothesis.strategies import integers
from pydantic import BaseConfig, ConstrainedSet, conset
from pydantic.fields import ModelField

from polyfactory.exceptions import ParameterError
from polyfactory.factories.pydantic_factory import ModelFactory, PydanticFieldMeta
from polyfactory.value_generators.constrained_collections import (
    handle_constrained_collection,
)

if TYPE_CHECKING:
    from polyfactory.field_meta import FieldMeta


def create_model_field(
    item_type: Any,
    min_items: int = 0,
    max_items: Optional[int] = None,
) -> "FieldMeta":
    model_field = ModelField(
        name="",
        class_validators={},
        model_config=BaseConfig,
        type_=conset(
            min_items=min_items,
            max_items=max_items if max_items is not None else min_items + 1,
            item_type=item_type,
        ),
    )
    return PydanticFieldMeta.from_model_field(model_field=model_field, use_alias=True)


@given(
    integers(min_value=0, max_value=10),
    integers(min_value=0, max_value=10),
)
def test_handle_constrained_set_with_min_items_and_max_items(min_items: int, max_items: int) -> None:
    field = create_model_field(str, min_items=min_items, max_items=max_items)
    assert issubclass(field.annotation, ConstrainedSet)
    if max_items >= min_items:
        result = handle_constrained_collection(
            collection_type=list,
            factory=ModelFactory,
            field_meta=field,
            item_type=str,
            max_items=field.annotation.max_items,
            min_items=field.annotation.min_items,
        )
        assert len(result) >= min_items
        assert len(result) <= max_items
    else:
        with pytest.raises(ParameterError):
            handle_constrained_collection(
                collection_type=list,
                factory=ModelFactory,
                field_meta=field,
                item_type=str,
                max_items=field.annotation.max_items,
                min_items=field.annotation.min_items,
            )


@given(
    integers(min_value=0, max_value=10),
)
def test_handle_constrained_set_with_max_items(
    max_items: int,
) -> None:
    field = create_model_field(str, max_items=max_items)
    assert issubclass(field.annotation, ConstrainedSet)
    result = handle_constrained_collection(
        collection_type=list,
        factory=ModelFactory,
        field_meta=field,
        item_type=str,
        max_items=field.annotation.max_items,
        min_items=field.annotation.min_items,
    )
    assert len(result) <= max_items


@given(
    integers(min_value=0, max_value=10),
)
def test_handle_constrained_set_with_min_items(
    min_items: int,
) -> None:
    field = create_model_field(str, min_items=min_items)
    assert issubclass(field.annotation, ConstrainedSet)
    result = handle_constrained_collection(
        collection_type=list,
        factory=ModelFactory,
        field_meta=field,
        item_type=str,
        max_items=field.annotation.max_items,
        min_items=field.annotation.min_items,
    )
    assert len(result) >= min_items


def test_handle_constrained_set_with_different_types() -> None:
    with suppress(ParameterError):
        for t_type in ModelFactory.get_provider_map():
            field = create_model_field(t_type, min_items=1)
            assert issubclass(field.annotation, ConstrainedSet)
            result = handle_constrained_collection(
                collection_type=list,
                factory=ModelFactory,
                field_meta=field,
                item_type=str,
                max_items=field.annotation.max_items,
                min_items=field.annotation.min_items,
            )
            assert len(result) > 0
