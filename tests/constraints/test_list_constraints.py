import sys
from random import Random
from typing import Any, List

import pytest
from hypothesis import given
from hypothesis.strategies import integers

from pydantic import VERSION

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
def test_handle_constrained_list_with_min_items_and_max_items(min_items: int, max_items: int) -> None:
    if max_items >= min_items:
        result = handle_constrained_collection(
            collection_type=list,
            factory=ModelFactory,
            field_meta=FieldMeta(name="test", annotation=list, random=Random()),
            item_type=str,
            max_items=max_items,
            min_items=min_items,
        )
        assert len(result) >= min_items
        assert len(result) <= max_items or 1
    else:
        with pytest.raises(ParameterException):
            handle_constrained_collection(
                collection_type=list,
                factory=ModelFactory,
                field_meta=FieldMeta(name="test", annotation=list, random=Random()),
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
        field_meta=FieldMeta(name="test", annotation=list, random=Random()),
        item_type=str,
        max_items=max_items,
    )
    assert len(result) <= max_items or 1


@given(
    integers(min_value=0, max_value=10),
)
def test_handle_constrained_list_with_min_items(
    min_items: int,
) -> None:
    result = handle_constrained_collection(
        collection_type=list,
        factory=ModelFactory,
        field_meta=FieldMeta.from_type(List[str], name="test", random=Random()),
        item_type=str,
        min_items=min_items,
    )
    assert len(result) >= min_items


@pytest.mark.skipif(
    sys.version_info < (3, 9) and VERSION.startswith("2"),
    reason="fails on python 3.8 with pydantic v2",
)
@pytest.mark.parametrize("t_type", tuple(ModelFactory.get_provider_map()))
def test_handle_constrained_list_with_different_types(t_type: Any) -> None:
    field_meta = FieldMeta.from_type(List[t_type], name="test", random=Random())
    result = handle_constrained_collection(
        collection_type=list,
        factory=ModelFactory,
        field_meta=field_meta.children[0],  # type: ignore[index]
        item_type=t_type,
    )
    assert len(result) > 0


def test_handle_unique_items() -> None:
    field_meta = FieldMeta.from_type(List[str], name="test", random=Random(), constraints={"unique_items": True})
    result = handle_constrained_collection(
        collection_type=list,
        factory=ModelFactory,
        field_meta=field_meta.children[0],  # type: ignore[index]
        item_type=str,
        unique_items=True,
        min_items=2,
        max_items=2,
    )
    assert len(result) == 2
    assert len(set(result)) == 2
