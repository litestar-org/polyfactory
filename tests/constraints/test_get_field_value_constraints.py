from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Type, Union, cast

import pytest

from polyfactory.factories.base import BaseFactory
from polyfactory.field_meta import Constraints, FieldMeta


@pytest.mark.parametrize("t", (int, float, Decimal))
def test_numbers(t: Type[Union[int, float, Decimal]]) -> None:
    constraints: Constraints = {"ge": 1, "le": 20}
    field_meta = FieldMeta.from_type(t, "foo", constraints=constraints)
    value = BaseFactory.get_field_value(field_meta)

    assert value >= constraints["ge"]
    assert value <= constraints["le"]


@pytest.mark.parametrize("t", (str, bytes))
def test_str_and_bytes(t: Type[Union[str, bytes]]) -> None:
    constraints: Constraints = {"min_length": 20, "max_length": 45}
    field_meta = FieldMeta.from_type(t, "foo", constraints=constraints)
    value = BaseFactory.get_field_value(field_meta)

    assert len(value) >= constraints["min_length"]
    assert len(value) <= constraints["max_length"]


@pytest.mark.parametrize("t", (list[int], set[int], tuple[int], frozenset[int]))
def test_collections(t: Type[Union[tuple, list, set, frozenset]]) -> None:
    constraints: Constraints = {
        "min_length": 2,
        "max_length": 10,
    }
    field_meta = FieldMeta.from_type(t, "foo", constraints=constraints)
    value = BaseFactory.get_field_value(field_meta)

    assert len(value) >= constraints["min_length"]
    assert len(value) <= constraints["max_length"]


def test_date() -> None:
    ge_date = datetime.today().date()
    le_date = ge_date + timedelta(days=10)
    constraints = {"ge": ge_date, "le": le_date}

    field_meta = FieldMeta.from_type(date, "foo", constraints=cast(Constraints, constraints))
    value = BaseFactory.get_field_value(field_meta)

    assert value >= ge_date
    assert value <= le_date
