from dataclasses import dataclass
from typing import Annotated

import pytest
from annotated_types import Len, MaxLen, MinLen

from polyfactory.factories import DataclassFactory
from polyfactory.field_meta import FieldMeta


class _LegacyV1Style:
    """Stand-in for a pydantic v1 style metadata object that only exposes ``min_items``/``max_items``."""

    min_items = 2
    max_items = 5


def test_parse_constraints_reads_min_and_max_length() -> None:
    class _Meta:
        min_length = 1
        max_length = 4

    constraints = FieldMeta.parse_constraints([_Meta()])

    assert constraints["min_length"] == 1
    assert constraints["max_length"] == 4


def test_parse_constraints_ignores_legacy_item_attributes() -> None:
    constraints = FieldMeta.parse_constraints([_LegacyV1Style()])

    assert "min_length" not in constraints
    assert "max_length" not in constraints


@pytest.mark.parametrize(
    ("metadata", "expected"),
    [
        (MinLen(2), {"min_length": 2}),
        (MaxLen(7), {"max_length": 7}),
        (Len(2, 7), {"min_length": 2, "max_length": 7}),
    ],
)
def test_parse_constraints_annotated_types_length(metadata: object, expected: dict) -> None:
    assert FieldMeta.parse_constraints([metadata]) == expected


def test_annotated_list_length_is_respected() -> None:
    @dataclass
    class Model:
        values: Annotated[list[int], Len(2, 3)]

    class ModelFactory(DataclassFactory[Model]):
        __model__ = Model

    for _ in range(20):
        assert 2 <= len(ModelFactory.build().values) <= 3
