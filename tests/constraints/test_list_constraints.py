import pytest

from polyfactory.exceptions import ParameterException
from polyfactory.factories.pydantic_factory import ModelFactory
from polyfactory.field_meta import FieldMeta
from polyfactory.value_generators.constrained_collections import (
    handle_constrained_collection,
)

# FIXME: issue due to pydantic v2 removing the hypothesis plugin.
try:
    from hypothesis import given
    from hypothesis.strategies import integers

except ImportError:
    given = None  # type: ignore
    integers = None  # type: ignore

    pytest.importorskip("hypothesis")


@given(
    integers(min_value=0, max_value=10),
    integers(min_value=0, max_value=10),
)
def test_handle_constrained_list_with_min_items_and_max_items(min_items: int, max_items: int) -> None:
    if max_items >= min_items:
        result = handle_constrained_collection(
            collection_type=list,
            factory=ModelFactory,
            field_meta=FieldMeta(name="test", annotation=list),
            item_type=str,
            max_items=max_items,
            min_items=min_items,
        )
        assert len(result) >= min_items
        assert len(result) <= max_items
    else:
        with pytest.raises(ParameterException):
            handle_constrained_collection(
                collection_type=list,
                factory=ModelFactory,
                field_meta=FieldMeta(name="test", annotation=list),
                item_type=str,
                max_items=max_items,
                min_items=min_items,
            )


@given(
    integers(min_value=0, max_value=10),
)
def test_handle_constrained_list_with_max_items(
    max_items: int,
) -> None:
    result = handle_constrained_collection(
        collection_type=list,
        factory=ModelFactory,
        field_meta=FieldMeta(name="test", annotation=list),
        item_type=str,
        max_items=max_items,
    )
    assert len(result) <= max_items


@given(
    integers(min_value=0, max_value=10),
)
def test_handle_constrained_list_with_min_items(
    min_items: int,
) -> None:
    result = handle_constrained_collection(
        collection_type=list,
        factory=ModelFactory,
        field_meta=FieldMeta(name="test", annotation=list),
        item_type=str,
        min_items=min_items,
    )
    assert len(result) >= min_items


def test_handle_constrained_list_with_different_types() -> None:
    for t_type in ModelFactory.get_provider_map():
        result = handle_constrained_collection(
            collection_type=list,
            factory=ModelFactory,
            field_meta=FieldMeta(name="test", annotation=list),
            item_type=t_type,
        )
        assert len(result) > 0


def test_handle_unique_items() -> None:
    result = handle_constrained_collection(
        collection_type=list,
        factory=ModelFactory,
        field_meta=FieldMeta(name="test", annotation=list),
        item_type=str,
        unique_items=True,
    )
    assert len(result) == 2
    assert len(set(result)) == 2
