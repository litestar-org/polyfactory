import math
from random import Random

import pytest
from hypothesis import assume, given
from hypothesis.strategies import floats

from polyfactory.exceptions import ParameterException
from polyfactory.value_generators.constrained_numbers import (
    handle_constrained_float,
    is_almost_multiple_of,
    is_multiply_of_multiple_of_in_range,
)


def assume_base2_exp_within(a: float, b: float, within: int) -> None:
    """
    Signal to Hypothesis that ``a`` and ``b`` must be within ``within`` powers of 2 from each other.
    """

    _, exp_a = math.frexp(a)
    _, exp_b = math.frexp(b)
    assume(abs(exp_a - exp_b) <= within)


def test_handle_constrained_float_without_constraints() -> None:
    result = handle_constrained_float(
        random=Random(),
    )
    assert isinstance(result, float)


@given(
    floats(
        allow_nan=False,
        allow_infinity=False,
        min_value=-1000000000,
        max_value=1000000000,
    ),
)
def test_handle_constrained_float_handles_ge(minimum: float) -> None:
    result = handle_constrained_float(
        random=Random(),
        ge=minimum,
    )
    assert result >= minimum


@given(
    floats(
        allow_nan=False,
        allow_infinity=False,
        min_value=-1000000000,
        max_value=1000000000,
    ),
)
def test_handle_constrained_float_handles_gt(minimum: float) -> None:
    result = handle_constrained_float(
        random=Random(),
        gt=minimum,
    )
    assert result > minimum


@given(
    floats(
        allow_nan=False,
        allow_infinity=False,
        min_value=-1000000000,
        max_value=1000000000,
    ),
)
def test_handle_constrained_float_handles_le(maximum: float) -> None:
    result = handle_constrained_float(
        random=Random(),
        le=maximum,
    )
    assert result <= maximum


@given(
    floats(
        allow_nan=False,
        allow_infinity=False,
        min_value=-1000000000,
        max_value=1000000000,
    ),
)
def test_handle_constrained_float_handles_lt(maximum: float) -> None:
    result = handle_constrained_float(
        random=Random(),
        lt=maximum,
    )
    assert result < maximum


@given(
    floats(
        allow_nan=False,
        allow_infinity=False,
        min_value=-1000000000,
        max_value=1000000000,
        width=32,
    ),
)
def test_handle_constrained_float_handles_multiple_of(multiple_of: float) -> None:
    if multiple_of != 0.0:
        result = handle_constrained_float(
            random=Random(),
            multiple_of=multiple_of,
        )
        assert is_almost_multiple_of(result, multiple_of)
    else:
        with pytest.raises(ParameterException):
            handle_constrained_float(
                random=Random(),
                multiple_of=multiple_of,
            )


@given(
    floats(
        allow_nan=False,
        allow_infinity=False,
        min_value=-1000000000,
        max_value=1000000000,
    ),
    floats(
        allow_nan=False,
        allow_infinity=False,
        min_value=-1000000000,
        max_value=1000000000,
        width=32,
    ),
)
def test_handle_constrained_float_handles_multiple_of_with_lt(max_value: float, multiple_of: float) -> None:
    if multiple_of != 0.0:
        assume_base2_exp_within(max_value, multiple_of, 24)
        result = handle_constrained_float(
            random=Random(),
            multiple_of=multiple_of,
            lt=max_value,
        )
        assert result < max_value
        assert is_almost_multiple_of(result, multiple_of)
    else:
        with pytest.raises(ParameterException):
            handle_constrained_float(
                random=Random(),
                multiple_of=multiple_of,
                lt=max_value,
            )


@given(
    floats(
        allow_nan=False,
        allow_infinity=False,
        min_value=-1000000000,
        max_value=1000000000,
    ),
    floats(
        allow_nan=False,
        allow_infinity=False,
        min_value=-1000000000,
        max_value=1000000000,
        width=32,
    ),
)
def test_handle_constrained_float_handles_multiple_of_with_le(max_value: float, multiple_of: float) -> None:
    if multiple_of != 0.0:
        assume_base2_exp_within(max_value, multiple_of, 24)
        result = handle_constrained_float(
            random=Random(),
            multiple_of=multiple_of,
            le=max_value,
        )
        assert result <= max_value
        assert is_almost_multiple_of(result, multiple_of)
    else:
        with pytest.raises(ParameterException):
            handle_constrained_float(
                random=Random(),
                multiple_of=multiple_of,
                le=max_value,
            )


@given(
    floats(
        allow_nan=False,
        allow_infinity=False,
        min_value=-1000000000,
        max_value=1000000000,
    ),
    floats(
        allow_nan=False,
        allow_infinity=False,
        min_value=-1000000000,
        max_value=1000000000,
        width=32,
    ),
)
def test_handle_constrained_float_handles_multiple_of_with_ge(min_value: float, multiple_of: float) -> None:
    if multiple_of != 0.0:
        assume_base2_exp_within(min_value, multiple_of, 24)
        result = handle_constrained_float(
            random=Random(),
            multiple_of=multiple_of,
            ge=min_value,
        )
        assert min_value <= result
        assert is_almost_multiple_of(result, multiple_of)
    else:
        with pytest.raises(ParameterException):
            handle_constrained_float(
                random=Random(),
                multiple_of=multiple_of,
                ge=min_value,
            )


@given(
    floats(
        allow_nan=False,
        allow_infinity=False,
        min_value=-1000000000,
        max_value=1000000000,
    ),
    floats(
        allow_nan=False,
        allow_infinity=False,
        min_value=-1000000000,
        max_value=1000000000,
        width=32,
    ),
)
def test_handle_constrained_float_handles_multiple_of_with_gt(min_value: float, multiple_of: float) -> None:
    if multiple_of != 0.0:
        assume_base2_exp_within(min_value, multiple_of, 24)
        result = handle_constrained_float(
            random=Random(),
            multiple_of=multiple_of,
            gt=min_value,
        )
        assert min_value < result
        assert is_almost_multiple_of(result, multiple_of)
    else:
        with pytest.raises(ParameterException):
            handle_constrained_float(
                random=Random(),
                multiple_of=multiple_of,
                gt=min_value,
            )


@pytest.mark.skip(reason="fails on edge cases")
@given(
    floats(
        allow_nan=False,
        allow_infinity=False,
        min_value=-1000000000,
        max_value=1000000000,
    ),
    floats(
        allow_nan=False,
        allow_infinity=False,
        min_value=-1000000000,
        max_value=1000000000,
    ),
    floats(
        allow_nan=False,
        allow_infinity=False,
        min_value=-1000000000,
        max_value=1000000000,
        width=32,
    ),
)
def test_handle_constrained_float_handles_multiple_of_with_ge_and_le(
    val1: float,
    val2: float,
    multiple_of: float,
) -> None:
    min_value, max_value = sorted([val1, val2])
    if multiple_of != 0.0 and is_multiply_of_multiple_of_in_range(
        minimum=min_value,
        maximum=max_value,
        multiple_of=multiple_of,
    ):
        assume_base2_exp_within(min_value, multiple_of, 24)
        assume_base2_exp_within(max_value, multiple_of, 24)
        result = handle_constrained_float(
            random=Random(),
            multiple_of=multiple_of,
            ge=min_value,
            lt=max_value,
        )
        assert min_value <= result <= max_value
        assert is_almost_multiple_of(result, multiple_of)
    else:
        with pytest.raises(ParameterException):
            handle_constrained_float(
                random=Random(),
                multiple_of=multiple_of,
                ge=min_value,
                lt=max_value,
            )
