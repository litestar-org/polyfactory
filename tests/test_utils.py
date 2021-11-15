import pytest
from faker import Faker
from hypothesis import given
from hypothesis.errors import InvalidArgument
from hypothesis.strategies import floats
from pydantic import confloat

from pydantic_factories.utils import handle_constrained_float

faker = Faker()


def test_handle_constrained_float_without_constraints():
    result = handle_constrained_float(confloat(), faker)
    assert isinstance(result, float)


@given(floats(allow_nan=False, allow_infinity=False, min_value=-1000000000, max_value=1000000000))
def test_handle_constrained_float_handles_ge(minimum):
    result = handle_constrained_float(confloat(ge=minimum), faker)
    assert result >= minimum


@given(floats(allow_nan=False, allow_infinity=False, min_value=-1000000000, max_value=1000000000))
def test_handle_constrained_float_handles_gt(minimum):
    result = handle_constrained_float(confloat(gt=minimum), faker)
    assert result > minimum


@given(floats(allow_nan=False, allow_infinity=False, min_value=-1000000000, max_value=1000000000))
def test_handle_constrained_float_handles_le(maximum):
    result = handle_constrained_float(confloat(le=maximum), faker)
    assert result <= maximum


@given(floats(allow_nan=False, allow_infinity=False, min_value=-1000000000, max_value=1000000000))
def test_handle_constrained_float_handles_lt(maximum):
    result = handle_constrained_float(confloat(lt=maximum), faker)
    assert result < maximum


@given(floats(allow_nan=False, allow_infinity=False, min_value=-1000000000, max_value=1000000000))
def test_handle_constrained_float_handles_multiple_of(multiple_of):
    result = handle_constrained_float(confloat(multiple_of=multiple_of), faker)
    assert result % multiple_of == 0 if multiple_of != 0 else True


def test_handle_constrained_float_handles_multiple_of_zero_value():
    # due to a bug in the pydantic hypothesis plugin, this code can only be tested in isolation
    # see: https://github.com/samuelcolvin/pydantic/issues/3418
    assert handle_constrained_float(confloat(multiple_of=0), faker) == 0


@given(
    floats(allow_nan=False, allow_infinity=False, min_value=-1000000000, max_value=1000000000),
    floats(allow_nan=False, allow_infinity=False, min_value=-1000000000, max_value=1000000000),
)
def test_handle_constrained_float_handles_multiple_of_with_lt(val1, val2):
    multiple_of, max_value = sorted([val1, val2])
    if multiple_of != 0:
        if multiple_of < max_value:
            result = handle_constrained_float(confloat(multiple_of=multiple_of, lt=max_value), faker)
            assert result % multiple_of == 0 if multiple_of != 0 else True
        else:
            with pytest.raises(AssertionError):
                handle_constrained_float(confloat(multiple_of=multiple_of, lt=max_value), faker)


@given(
    floats(allow_nan=False, allow_infinity=False, min_value=-1000000000, max_value=1000000000),
    floats(allow_nan=False, allow_infinity=False, min_value=-1000000000, max_value=1000000000),
)
def test_handle_constrained_float_handles_multiple_of_with_le(val1, val2):
    multiple_of, max_value = sorted([val1, val2])
    if multiple_of != 0:
        if multiple_of < max_value:
            result = handle_constrained_float(confloat(multiple_of=multiple_of, le=max_value), faker)
            assert result % multiple_of == 0
        else:
            with pytest.raises(AssertionError):
                handle_constrained_float(confloat(multiple_of=multiple_of, le=max_value), faker)


@given(
    floats(allow_nan=False, allow_infinity=False, min_value=-1000000000, max_value=1000000000),
    floats(allow_nan=False, allow_infinity=False, min_value=-1000000000, max_value=1000000000),
)
def test_handle_constrained_float_handles_multiple_of_with_ge(val1, val2):
    min_value, multiple_of = sorted([val1, val2])
    if multiple_of != 0:
        result = handle_constrained_float(confloat(multiple_of=multiple_of, ge=min_value), faker)
        assert result % multiple_of == 0


@given(
    floats(allow_nan=False, allow_infinity=False, min_value=-1000000000, max_value=1000000000),
    floats(allow_nan=False, allow_infinity=False, min_value=-1000000000, max_value=1000000000),
)
def test_handle_constrained_float_handles_multiple_of_with_gt(val1, val2):
    min_value, multiple_of = sorted([val1, val2])
    if multiple_of != 0:
        result = handle_constrained_float(confloat(multiple_of=multiple_of, gt=min_value), faker)
        assert result % multiple_of == 0


@given(
    floats(allow_nan=False, allow_infinity=False, min_value=-1000000000, max_value=1000000000),
    floats(allow_nan=False, allow_infinity=False, min_value=-1000000000, max_value=1000000000),
    floats(allow_nan=False, allow_infinity=False, min_value=-1000000000, max_value=1000000000),
)
def test_handle_constrained_float_handles_multiple_of_with_ge_and_le(val1, val2, val3):
    min_value, multiple_of, max_value = sorted([val1, val2, val3])
    try:
        if round(multiple_of) != 0:
            if multiple_of < max_value and min_value < max_value:
                result = handle_constrained_float(confloat(multiple_of=multiple_of, ge=min_value, le=max_value), faker)
                assert round(result, 2) % round(multiple_of, 2) == 0
            else:
                with pytest.raises(AssertionError):
                    handle_constrained_float(confloat(multiple_of=multiple_of, ge=min_value, le=max_value), faker)
    except InvalidArgument:
        # again, a pydantic / hypothesis error
        pass
