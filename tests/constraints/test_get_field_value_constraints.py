from datetime import date, datetime, timedelta
from decimal import Decimal
from random import Random
from typing import FrozenSet, List, Set, Tuple, Type, Union, cast

import pytest
from typing_extensions import Annotated

from polyfactory.factories.base import BaseFactory
from polyfactory.field_meta import Constraints, FieldMeta


@pytest.mark.parametrize("t", (int, float, Decimal))
def test_numbers(t: Type[Union[int, float, Decimal]]) -> None:
    constraints: Constraints = {"ge": 1, "le": 20}
    field_meta = FieldMeta.from_type(annotation=t, name="foo", constraints=constraints, random=Random())
    value = BaseFactory.get_field_value(field_meta)

    assert value >= constraints["ge"]
    assert value <= constraints["le"]


@pytest.mark.parametrize("t", (str, bytes))
def test_str_and_bytes(t: Type[Union[str, bytes]]) -> None:
    constraints: Constraints = {"min_length": 20, "max_length": 45}
    field_meta = FieldMeta.from_type(annotation=t, name="foo", constraints=constraints, random=Random())
    value = BaseFactory.get_field_value(field_meta)

    assert len(value) >= constraints["min_length"]
    assert len(value) <= constraints["max_length"]


@pytest.mark.parametrize("t", (List[int], Set[int], Tuple[int], FrozenSet[int]))
def test_collections(t: Type[Union[Tuple, List, Set, FrozenSet]]) -> None:
    constraints: Constraints = {
        "min_length": 2,
        "max_length": 10,
    }
    field_meta = FieldMeta.from_type(annotation=t, name="foo", constraints=constraints, random=Random())
    value = BaseFactory.get_field_value(field_meta)

    assert len(value) >= constraints["min_length"]
    assert len(value) <= constraints["max_length"]


def test_date() -> None:
    ge_date = datetime.now().date()
    le_date = ge_date + timedelta(days=10)
    constraints = {"ge": ge_date, "le": le_date}

    field_meta = FieldMeta.from_type(
        annotation=date,
        name="foo",
        constraints=cast(Constraints, constraints),
        random=Random(),
    )
    value = BaseFactory.get_field_value(field_meta)

    assert value >= ge_date
    assert value <= le_date


def test_constraints_parsing() -> None:
    constraints = Constraints(min_length=10)
    annotation = Annotated[str, constraints]
    field_meta = FieldMeta.from_type(annotation)

    assert field_meta.constraints == constraints
