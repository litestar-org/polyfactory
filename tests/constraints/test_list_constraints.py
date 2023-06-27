from typing import TYPE_CHECKING, Any, Optional

import pytest
from hypothesis import given
from hypothesis.strategies import integers
from pydantic import BaseConfig, ConstrainedList, conlist
from pydantic.fields import ModelField

from polyfactory.exceptions import ParameterException
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
    unique_items: bool = False,
) -> "FieldMeta":
    model_field = ModelField(
        name="",
        class_validators={},
        model_config=BaseConfig,
        type_=conlist(
            min_items=min_items,
            max_items=max_items if max_items is not None else min_items + 1,
            unique_items=unique_items,
            item_type=item_type,
        ),
    )
    return PydanticFieldMeta.from_model_field(model_field=model_field, use_alias=False)


@given(
    integers(min_value=0, max_value=10),
    integers(min_value=0, max_value=10),
)
def test_handle_constrained_list_with_min_items_and_max_items(min_items: int, max_items: int) -> None:
    field = create_model_field(str, min_items=min_items, max_items=max_items)
    assert issubclass(field.annotation, ConstrainedList)
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
        with pytest.raises(ParameterException):
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
def test_handle_constrained_list_with_max_items(
    max_items: int,
) -> None:
    field = create_model_field(str, max_items=max_items)
    assert issubclass(field.annotation, ConstrainedList)
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
def test_handle_constrained_list_with_min_items(
    min_items: int,
) -> None:
    field = create_model_field(str, min_items=min_items)
    assert issubclass(field.annotation, ConstrainedList)
    result = handle_constrained_collection(
        collection_type=list,
        factory=ModelFactory,
        field_meta=field,
        item_type=str,
        max_items=field.annotation.max_items,
        min_items=field.annotation.min_items,
    )
    assert len(result) >= min_items


def test_handle_constrained_list_with_different_types() -> None:
    for t_type in ModelFactory.get_provider_map():
        field = create_model_field(t_type, min_items=1)
        assert issubclass(field.annotation, ConstrainedList)
        result = handle_constrained_collection(
            collection_type=list,
            factory=ModelFactory,
            field_meta=field.children[0] if field.children else field,
            item_type=t_type,
            max_items=field.annotation.max_items,
            min_items=field.annotation.min_items,
        )
        assert len(result) > 0


def test_handle_unique_items() -> None:
    field = create_model_field(bool, min_items=2, max_items=2, unique_items=True)
    assert issubclass(field.annotation, ConstrainedList)
    result = handle_constrained_collection(
        collection_type=list,
        factory=ModelFactory,
        field_meta=field.children[0] if field.children else field,
        item_type=str,
        max_items=field.annotation.max_items,
        min_items=field.annotation.min_items,
        unique_items=True,
    )
    assert len(result) == 2
    assert len(set(result)) == 2
