import pytest
from hypothesis import given
from hypothesis.strategies import integers

from polyfactory.exceptions import ParameterException
from polyfactory.factories.pydantic_factory import ModelFactory, PydanticFieldMeta
from polyfactory.value_generators.constrained_collections import (
    handle_constrained_mapping,
)


@given(
    integers(min_value=0, max_value=10),
    integers(min_value=0, max_value=10),
)
def test_handle_constrained_mapping_with_min_items_and_max_items(min_items: int, max_items: int) -> None:
    key_field = PydanticFieldMeta(name="key", annotation=str)
    value_field = PydanticFieldMeta(name="value", annotation=int)
    field_meta = PydanticFieldMeta(name="test", annotation=dict, children=[key_field, value_field])

    if max_items >= min_items:
        result = handle_constrained_mapping(
            factory=ModelFactory,
            field_meta=field_meta,
            max_items=max_items,
            min_items=min_items,
        )
        assert len(result) >= min_items
        assert len(result) <= max_items or 1
        for key, value in result.items():
            assert isinstance(key, str)
            assert isinstance(value, int)
    else:
        with pytest.raises(ParameterException):
            handle_constrained_mapping(
                factory=ModelFactory,
                field_meta=field_meta,
                max_items=max_items,
                min_items=min_items,
            )


def test_handle_constrained_mapping_with_constrained_key_and_value() -> None:
    key_min_length = 5
    value_gt = 100
    min_length = 5
    max_length = 10

    key_field = PydanticFieldMeta(name="key", annotation=str, constraints={"min_length": key_min_length})
    value_field = PydanticFieldMeta(name="value", annotation=int, constraints={"gt": value_gt})
    field_meta = PydanticFieldMeta(name="test", annotation=dict, children=[key_field, value_field])

    result = handle_constrained_mapping(
        factory=ModelFactory,
        field_meta=field_meta,
        min_items=min_length,
        max_items=max_length,
    )

    assert len(result) >= min_length
    assert len(result) <= max_length

    for key, value in result.items():
        assert isinstance(key, str)
        assert isinstance(value, int)

        assert len(key) >= key_min_length
        assert value >= value_gt
