from typing import Optional

import pytest
from hypothesis import given
from hypothesis.strategies import integers
from pydantic import ConstrainedInt

from pydantic_factories.constraints.integer import handle_constrained_int
from pydantic_factories.utils import passes_pydantic_multiple_validator


def create_constrained_field(
    gt: Optional[int] = None,
    ge: Optional[int] = None,
    lt: Optional[int] = None,
    le: Optional[int] = None,
    multiple_of: Optional[int] = None,
) -> ConstrainedInt:
    field = ConstrainedInt()
    field.ge = ge
    field.gt = gt
    field.lt = lt
    field.le = le
    field.multiple_of = multiple_of
    return field


def test_handle_constrained_int_without_constraints() -> None:
    result = handle_constrained_int(create_constrained_field())
    assert isinstance(result, int)


@given(integers(min_value=-1000000000, max_value=1000000000))
def test_handle_constrained_int_handles_ge(minimum: int) -> None:
    result = handle_constrained_int(create_constrained_field(ge=minimum))
    assert result >= minimum


@given(integers(min_value=-1000000000, max_value=1000000000))
def test_handle_constrained_int_handles_gt(minimum: int) -> None:
    result = handle_constrained_int(create_constrained_field(gt=minimum))
    assert result > minimum


@given(integers(min_value=-1000000000, max_value=1000000000))
def test_handle_constrained_int_handles_le(maximum: int) -> None:
    result = handle_constrained_int(create_constrained_field(le=maximum))
    assert result <= maximum


@given(integers(min_value=-1000000000, max_value=1000000000))
def test_handle_constrained_int_handles_lt(maximum: int) -> None:
    result = handle_constrained_int(create_constrained_field(lt=maximum))
    assert result < maximum


@given(integers(min_value=-1000000000, max_value=1000000000))
def test_handle_constrained_int_handles_multiple_of(multiple_of: int) -> None:
    result = handle_constrained_int(create_constrained_field(multiple_of=multiple_of))
    assert passes_pydantic_multiple_validator(result, multiple_of)


@given(
    integers(min_value=-1000000000, max_value=1000000000),
    integers(min_value=-1000000000, max_value=1000000000),
)
def test_handle_constrained_int_handles_multiple_of_with_lt(val1: int, val2: int) -> None:
    multiple_of, max_value = sorted([val1, val2])
    if multiple_of < max_value - 1 or multiple_of == 0:
        result = handle_constrained_int(create_constrained_field(multiple_of=multiple_of, lt=max_value))
        assert passes_pydantic_multiple_validator(result, multiple_of)
    else:
        with pytest.raises(AssertionError):
            handle_constrained_int(create_constrained_field(multiple_of=multiple_of, lt=max_value))


@given(
    integers(min_value=-1000000000, max_value=1000000000),
    integers(min_value=-1000000000, max_value=1000000000),
)
def test_handle_constrained_int_handles_multiple_of_with_le(val1: int, val2: int) -> None:
    multiple_of, max_value = sorted([val1, val2])
    if multiple_of < max_value or multiple_of == 0:
        result = handle_constrained_int(create_constrained_field(multiple_of=multiple_of, le=max_value))
        assert passes_pydantic_multiple_validator(result, multiple_of)
    else:
        with pytest.raises(AssertionError):
            handle_constrained_int(create_constrained_field(multiple_of=multiple_of, le=max_value))


@given(
    integers(min_value=-1000000000, max_value=1000000000),
    integers(min_value=-1000000000, max_value=1000000000),
)
def test_handle_constrained_int_handles_multiple_of_with_ge(val1: int, val2: int) -> None:
    min_value, multiple_of = sorted([val1, val2])
    result = handle_constrained_int(create_constrained_field(multiple_of=multiple_of, ge=min_value))
    assert passes_pydantic_multiple_validator(result, multiple_of)


@given(
    integers(min_value=-1000000000, max_value=1000000000),
    integers(min_value=-1000000000, max_value=1000000000),
)
def test_handle_constrained_int_handles_multiple_of_with_gt(val1: int, val2: int) -> None:
    min_value, multiple_of = sorted([val1, val2])
    result = handle_constrained_int(create_constrained_field(multiple_of=multiple_of, gt=min_value))
    assert passes_pydantic_multiple_validator(result, multiple_of)


@given(
    integers(min_value=-1000000000, max_value=1000000000),
    integers(min_value=-1000000000, max_value=1000000000),
    integers(min_value=-1000000000, max_value=1000000000),
)
def test_handle_constrained_int_handles_multiple_of_with_ge_and_le(val1: int, val2: int, val3: int) -> None:
    min_value, multiple_of, max_value = sorted([val1, val2, val3])
    if multiple_of < max_value and min_value < max_value or multiple_of == 0:
        result = handle_constrained_int(create_constrained_field(multiple_of=multiple_of, ge=min_value, le=max_value))
        assert passes_pydantic_multiple_validator(result, multiple_of)
    else:
        with pytest.raises(AssertionError):
            handle_constrained_int(create_constrained_field(multiple_of=multiple_of, ge=min_value, le=max_value))


@given(
    integers(min_value=-1000000000, max_value=1000000000),
    integers(min_value=-1000000000, max_value=1000000000),
    integers(min_value=-1000000000, max_value=1000000000),
)
def test_handle_constrained_int_handles_ge_and_le_with_lower_multiple_of(val1: int, val2: int, val3: int) -> None:
    multiple_of, min_value, max_value = sorted([val1, val2, val3])
    if multiple_of == 0 or multiple_of < max_value and min_value < max_value:
        result = handle_constrained_int(create_constrained_field(multiple_of=multiple_of, ge=min_value, le=max_value))
        assert passes_pydantic_multiple_validator(result, multiple_of)
    else:
        with pytest.raises(AssertionError):
            handle_constrained_int(create_constrained_field(multiple_of=multiple_of, ge=min_value, le=max_value))
