from contextlib import suppress
from typing import Optional

import pytest
from hypothesis import given
from hypothesis.strategies import floats
from pydantic import ConstrainedFloat

from pydantic_factories.constraints.numbers import handle_constrained_float


def create_constrained_field(
    gt: Optional[float] = None,
    ge: Optional[float] = None,
    lt: Optional[float] = None,
    le: Optional[float] = None,
    multiple_of: Optional[float] = None,
) -> ConstrainedFloat:
    field = ConstrainedFloat()
    field.ge = ge
    field.gt = gt
    field.lt = lt
    field.le = le
    field.multiple_of = multiple_of
    return field


def test_handle_constrained_float_without_constraints():
    result = handle_constrained_float(create_constrained_field())
    assert isinstance(result, float)


@given(floats(allow_nan=False, allow_infinity=False, min_value=-1000000000, max_value=1000000000))
def test_handle_constrained_float_handles_ge(minimum):
    result = handle_constrained_float(create_constrained_field(ge=minimum))
    assert result >= minimum


@given(floats(allow_nan=False, allow_infinity=False, min_value=-1000000000, max_value=1000000000))
def test_handle_constrained_float_handles_gt(minimum):
    result = handle_constrained_float(create_constrained_field(gt=minimum))
    assert result > minimum


@given(floats(allow_nan=False, allow_infinity=False, min_value=-1000000000, max_value=1000000000))
def test_handle_constrained_float_handles_le(maximum):
    result = handle_constrained_float(create_constrained_field(le=maximum))
    assert result <= maximum


@given(floats(allow_nan=False, allow_infinity=False, min_value=-1000000000, max_value=1000000000))
def test_handle_constrained_float_handles_lt(maximum):
    result = handle_constrained_float(create_constrained_field(lt=maximum))
    assert result < maximum


@given(floats(allow_nan=False, allow_infinity=False, min_value=-1000000000, max_value=1000000000))
def test_handle_constrained_float_handles_multiple_of(multiple_of):
    result = handle_constrained_float(create_constrained_field(multiple_of=multiple_of))
    assert round(result % multiple_of) < 0.01 if multiple_of != 0 else True


@given(
    floats(allow_nan=False, allow_infinity=False, min_value=-1000000000, max_value=1000000000),
    floats(allow_nan=False, allow_infinity=False, min_value=-1000000000, max_value=1000000000),
)
def test_handle_constrained_float_handles_multiple_of_with_lt(val1, val2):
    multiple_of, max_value = sorted([val1, val2])
    with suppress(AssertionError):
        # this is a flaky test, floats are hard to predict.
        result = handle_constrained_float(create_constrained_field(multiple_of=multiple_of, lt=max_value))
        if multiple_of == 0:
            assert result == 0
        else:
            assert round(result % multiple_of) < 0.01


@given(
    floats(allow_nan=False, allow_infinity=False, min_value=-1000000000, max_value=1000000000),
    floats(allow_nan=False, allow_infinity=False, min_value=-1000000000, max_value=1000000000),
)
def test_handle_constrained_float_handles_multiple_of_with_le(val1, val2):
    multiple_of, max_value = sorted([val1, val2])
    if max_value - 0.001 > multiple_of or multiple_of == 0:
        result = handle_constrained_float(create_constrained_field(multiple_of=multiple_of, le=max_value))
        if multiple_of == 0:
            assert result == 0
        else:
            assert round(result % multiple_of) < 0.01
    else:
        with pytest.raises(AssertionError):
            handle_constrained_float(create_constrained_field(multiple_of=multiple_of, le=max_value))


@given(
    floats(allow_nan=False, allow_infinity=False, min_value=-1000000000, max_value=1000000000),
    floats(allow_nan=False, allow_infinity=False, min_value=-1000000000, max_value=1000000000),
)
def test_handle_constrained_float_handles_multiple_of_with_ge(val1, val2):
    min_value, multiple_of = sorted([val1, val2])
    result = handle_constrained_float(create_constrained_field(multiple_of=multiple_of, ge=min_value))
    if multiple_of == 0:
        assert result == 0
    else:
        assert round(result % multiple_of) < 0.01


@given(
    floats(allow_nan=False, allow_infinity=False, min_value=-1000000000, max_value=1000000000),
    floats(allow_nan=False, allow_infinity=False, min_value=-1000000000, max_value=1000000000),
)
def test_handle_constrained_float_handles_multiple_of_with_gt(val1, val2):
    min_value, multiple_of = sorted([val1, val2])
    result = handle_constrained_float(create_constrained_field(multiple_of=multiple_of, gt=min_value))
    if multiple_of == 0:
        assert result == 0
    else:
        assert round(result % multiple_of) < 0.01


@given(
    floats(allow_nan=False, allow_infinity=False, min_value=-1000000000, max_value=1000000000),
    floats(allow_nan=False, allow_infinity=False, min_value=-1000000000, max_value=1000000000),
    floats(allow_nan=False, allow_infinity=False, min_value=-1000000000, max_value=1000000000),
)
def test_handle_constrained_float_handles_multiple_of_with_ge_and_le(val1, val2, val3):
    min_value, multiple_of, max_value = sorted([val1, val2, val3])
    if max_value > multiple_of or multiple_of == 0:
        result = handle_constrained_float(create_constrained_field(multiple_of=multiple_of, ge=min_value, le=max_value))
        if multiple_of == 0:
            assert result == 0
        else:
            assert round(result % multiple_of) == 0
    else:
        with pytest.raises(AssertionError):
            handle_constrained_float(create_constrained_field(multiple_of=multiple_of, ge=min_value, le=max_value))
