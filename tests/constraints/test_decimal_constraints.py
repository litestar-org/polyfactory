from decimal import Decimal
from typing import Optional

import pytest
from hypothesis import given
from hypothesis.strategies import decimals, integers
from pydantic import ConstrainedDecimal

from pydantic_factories.constraints.constrained_decimal_handler import (
    handle_constrained_decimal,
)
from tests.utils import passes_pydantic_multiple_validator


def create_constrained_field(
    gt: Optional[Decimal] = None,
    ge: Optional[Decimal] = None,
    lt: Optional[Decimal] = None,
    le: Optional[Decimal] = None,
    multiple_of: Optional[Decimal] = None,
    decimal_places: Optional[int] = None,
    max_digits: Optional[int] = None,
) -> ConstrainedDecimal:
    field = ConstrainedDecimal()
    field.ge = ge
    field.gt = gt
    field.lt = lt
    field.le = le
    field.multiple_of = multiple_of
    field.max_digits = max_digits
    field.decimal_places = decimal_places
    return field


def test_handle_constrained_decimal_without_constraints():
    result = handle_constrained_decimal(create_constrained_field())
    assert isinstance(result, Decimal)


@given(integers(min_value=0, max_value=100))
def test_handle_constrained_decimal_handles_max_digits(max_digits):
    if max_digits > 0:
        result = handle_constrained_decimal(create_constrained_field(max_digits=max_digits))
        assert len(result.as_tuple().digits) - abs(result.as_tuple().exponent) <= max_digits
    else:
        with pytest.raises(AssertionError):
            handle_constrained_decimal(create_constrained_field(max_digits=max_digits))


@given(integers(min_value=0, max_value=100))
def test_handle_constrained_decimal_handles_decimal_places(decimal_places):
    result = handle_constrained_decimal(create_constrained_field(decimal_places=decimal_places))
    assert abs(result.as_tuple().exponent) <= decimal_places


@given(integers(min_value=0, max_value=100), integers(min_value=1, max_value=100))
def test_handle_constrained_decimal_handles_max_digits_and_decimal_places(max_digits, decimal_places):
    if max_digits > 0 and decimal_places < max_digits:
        result = handle_constrained_decimal(
            create_constrained_field(max_digits=max_digits, decimal_places=decimal_places)
        )
        assert len(result.as_tuple().digits) - abs(result.as_tuple().exponent) <= max_digits
    else:
        with pytest.raises(AssertionError):
            handle_constrained_decimal(create_constrained_field(max_digits=max_digits, decimal_places=decimal_places))


@given(decimals(allow_nan=False, allow_infinity=False, min_value=-1000000000, max_value=1000000000))
def test_handle_constrained_decimal_handles_ge(minimum):
    result = handle_constrained_decimal(create_constrained_field(ge=minimum))
    assert result >= minimum


@given(decimals(allow_nan=False, allow_infinity=False, min_value=-1000000000, max_value=1000000000))
def test_handle_constrained_decimal_handles_gt(minimum):
    result = handle_constrained_decimal(create_constrained_field(gt=minimum))
    assert result > minimum


@given(decimals(allow_nan=False, allow_infinity=False, min_value=-1000000000, max_value=1000000000))
def test_handle_constrained_decimal_handles_le(maximum):
    result = handle_constrained_decimal(create_constrained_field(le=maximum))
    assert result <= maximum


@given(decimals(allow_nan=False, allow_infinity=False, min_value=-1000000000, max_value=1000000000))
def test_handle_constrained_decimal_handles_lt(maximum):
    result = handle_constrained_decimal(create_constrained_field(lt=maximum))
    assert result < maximum


@given(decimals(allow_nan=False, allow_infinity=False, min_value=-1000000000, max_value=1000000000))
def test_handle_constrained_decimal_handles_multiple_of(multiple_of):
    result = handle_constrained_decimal(create_constrained_field(multiple_of=multiple_of))
    assert passes_pydantic_multiple_validator(result, multiple_of)


@given(
    decimals(allow_nan=False, allow_infinity=False, min_value=-1000000000, max_value=1000000000),
    decimals(allow_nan=False, allow_infinity=False, min_value=-1000000000, max_value=1000000000),
)
def test_handle_constrained_decimal_handles_multiple_of_with_lt(val1, val2):
    multiple_of, max_value = sorted([val1, val2])
    if multiple_of == 0 or max_value - Decimal("0.001") > multiple_of:
        result = handle_constrained_decimal(create_constrained_field(multiple_of=multiple_of, lt=max_value))
        assert passes_pydantic_multiple_validator(result, multiple_of)
    else:
        with pytest.raises(AssertionError):
            handle_constrained_decimal(create_constrained_field(multiple_of=multiple_of, lt=max_value))


@given(
    decimals(allow_nan=False, allow_infinity=False, min_value=-1000000000, max_value=1000000000),
    decimals(allow_nan=False, allow_infinity=False, min_value=-1000000000, max_value=1000000000),
)
def test_handle_constrained_decimal_handles_multiple_of_with_le(val1, val2):
    multiple_of, max_value = sorted([val1, val2])
    if multiple_of == 0 or max_value > multiple_of:
        result = handle_constrained_decimal(create_constrained_field(multiple_of=multiple_of, le=max_value))
        assert passes_pydantic_multiple_validator(result, multiple_of)
    else:
        with pytest.raises(AssertionError):
            handle_constrained_decimal(create_constrained_field(multiple_of=multiple_of, le=max_value))


@given(
    decimals(allow_nan=False, allow_infinity=False, min_value=-1000000000, max_value=1000000000),
    decimals(allow_nan=False, allow_infinity=False, min_value=-1000000000, max_value=1000000000),
)
def test_handle_constrained_decimal_handles_multiple_of_with_ge(val1, val2):
    min_value, multiple_of = sorted([val1, val2])
    result = handle_constrained_decimal(create_constrained_field(multiple_of=multiple_of, ge=min_value))
    assert passes_pydantic_multiple_validator(result, multiple_of)


@given(
    decimals(allow_nan=False, allow_infinity=False, min_value=-1000000000, max_value=1000000000),
    decimals(allow_nan=False, allow_infinity=False, min_value=-1000000000, max_value=1000000000),
)
def test_handle_constrained_decimal_handles_multiple_of_with_gt(val1, val2):
    min_value, multiple_of = sorted([val1, val2])
    result = handle_constrained_decimal(create_constrained_field(multiple_of=multiple_of, gt=min_value))
    assert passes_pydantic_multiple_validator(result, multiple_of)


@given(
    decimals(allow_nan=False, allow_infinity=False, min_value=-1000000000, max_value=1000000000),
    decimals(allow_nan=False, allow_infinity=False, min_value=-1000000000, max_value=1000000000),
    decimals(allow_nan=False, allow_infinity=False, min_value=-1000000000, max_value=1000000000),
)
def test_handle_constrained_decimal_handles_multiple_of_with_ge_and_le(val1, val2, val3):
    min_value, multiple_of, max_value = sorted([val1, val2, val3])
    if max_value > multiple_of or multiple_of == 0:
        result = handle_constrained_decimal(
            create_constrained_field(multiple_of=multiple_of, ge=min_value, le=max_value)
        )
        assert passes_pydantic_multiple_validator(result, multiple_of)
    else:
        with pytest.raises(AssertionError):
            handle_constrained_decimal(create_constrained_field(multiple_of=multiple_of, ge=min_value, le=max_value))
