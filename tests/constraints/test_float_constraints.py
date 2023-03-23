from random import Random
from typing import Optional

import pytest
from hypothesis import given
from hypothesis.strategies import floats
from pydantic import ConstrainedFloat

from polyfactory.exceptions import ParameterError
from polyfactory.value_generators.constrained_numbers import (
    handle_constrained_float,
    is_multiply_of_multiple_of_in_range,
    passes_pydantic_multiple_validator,
)


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


def test_handle_constrained_float_without_constraints() -> None:
    constrained_field = create_constrained_field()
    result = handle_constrained_float(
        random=Random(),
        multiple_of=constrained_field.multiple_of,
        gt=constrained_field.gt,
        ge=constrained_field.ge,
        lt=constrained_field.lt,
        le=constrained_field.le,
    )
    assert isinstance(result, float)


@given(
    floats(
        allow_nan=False,
        allow_infinity=False,
        min_value=-1000000000,
        max_value=1000000000,
    )
)
def test_handle_constrained_float_handles_ge(minimum: float) -> None:
    constrained_field = create_constrained_field(ge=minimum)
    result = handle_constrained_float(
        random=Random(),
        multiple_of=constrained_field.multiple_of,
        gt=constrained_field.gt,
        ge=constrained_field.ge,
        lt=constrained_field.lt,
        le=constrained_field.le,
    )
    assert result >= minimum


@given(
    floats(
        allow_nan=False,
        allow_infinity=False,
        min_value=-1000000000,
        max_value=1000000000,
    )
)
def test_handle_constrained_float_handles_gt(minimum: float) -> None:
    constrained_field = create_constrained_field(gt=minimum)
    result = handle_constrained_float(
        random=Random(),
        multiple_of=constrained_field.multiple_of,
        gt=constrained_field.gt,
        ge=constrained_field.ge,
        lt=constrained_field.lt,
        le=constrained_field.le,
    )
    assert result > minimum


@given(
    floats(
        allow_nan=False,
        allow_infinity=False,
        min_value=-1000000000,
        max_value=1000000000,
    )
)
def test_handle_constrained_float_handles_le(maximum: float) -> None:
    constrained_field = create_constrained_field(le=maximum)
    result = handle_constrained_float(
        random=Random(),
        multiple_of=constrained_field.multiple_of,
        gt=constrained_field.gt,
        ge=constrained_field.ge,
        lt=constrained_field.lt,
        le=constrained_field.le,
    )
    assert result <= maximum


@given(
    floats(
        allow_nan=False,
        allow_infinity=False,
        min_value=-1000000000,
        max_value=1000000000,
    )
)
def test_handle_constrained_float_handles_lt(maximum: float) -> None:
    constrained_field = create_constrained_field(lt=maximum)
    result = handle_constrained_float(
        random=Random(),
        multiple_of=constrained_field.multiple_of,
        gt=constrained_field.gt,
        ge=constrained_field.ge,
        lt=constrained_field.lt,
        le=constrained_field.le,
    )
    assert result < maximum


@given(
    floats(
        allow_nan=False,
        allow_infinity=False,
        min_value=-1000000000,
        max_value=1000000000,
    )
)
def test_handle_constrained_float_handles_multiple_of(multiple_of: float) -> None:
    if multiple_of != 0.0:
        constrained_field = create_constrained_field(multiple_of=multiple_of)
        result = handle_constrained_float(
            random=Random(),
            multiple_of=constrained_field.multiple_of,
            gt=constrained_field.gt,
            ge=constrained_field.ge,
            lt=constrained_field.lt,
            le=constrained_field.le,
        )
        assert passes_pydantic_multiple_validator(result, multiple_of)
    else:
        with pytest.raises(ParameterError):
            constrained_field = create_constrained_field(multiple_of=multiple_of)
            handle_constrained_float(
                random=Random(),
                multiple_of=constrained_field.multiple_of,
                gt=constrained_field.gt,
                ge=constrained_field.ge,
                lt=constrained_field.lt,
                le=constrained_field.le,
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
    ),
)
def test_handle_constrained_float_handles_multiple_of_with_lt(val1: float, val2: float) -> None:
    multiple_of, max_value = sorted([val1, val2])
    if multiple_of != 0.0:
        constrained_field = create_constrained_field(multiple_of=multiple_of, lt=max_value)
        result = handle_constrained_float(
            random=Random(),
            multiple_of=constrained_field.multiple_of,
            gt=constrained_field.gt,
            ge=constrained_field.ge,
            lt=constrained_field.lt,
            le=constrained_field.le,
        )
        assert passes_pydantic_multiple_validator(result, multiple_of)
    else:
        with pytest.raises(ParameterError):
            constrained_field = create_constrained_field(multiple_of=multiple_of, lt=max_value)
            handle_constrained_float(
                random=Random(),
                multiple_of=constrained_field.multiple_of,
                gt=constrained_field.gt,
                ge=constrained_field.ge,
                lt=constrained_field.lt,
                le=constrained_field.le,
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
    ),
)
def test_handle_constrained_float_handles_multiple_of_with_le(val1: float, val2: float) -> None:
    multiple_of, max_value = sorted([val1, val2])
    if multiple_of != 0.0:
        constrained_field = create_constrained_field(multiple_of=multiple_of, le=max_value)
        result = handle_constrained_float(
            random=Random(),
            multiple_of=constrained_field.multiple_of,
            gt=constrained_field.gt,
            ge=constrained_field.ge,
            lt=constrained_field.lt,
            le=constrained_field.le,
        )
        assert passes_pydantic_multiple_validator(result, multiple_of)
    else:
        with pytest.raises(ParameterError):
            constrained_field = create_constrained_field(multiple_of=multiple_of, le=max_value)
            handle_constrained_float(
                random=Random(),
                multiple_of=constrained_field.multiple_of,
                gt=constrained_field.gt,
                ge=constrained_field.ge,
                lt=constrained_field.lt,
                le=constrained_field.le,
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
    ),
)
def test_handle_constrained_float_handles_multiple_of_with_ge(val1: float, val2: float) -> None:
    min_value, multiple_of = sorted([val1, val2])
    if multiple_of != 0.0:
        constrained_field = create_constrained_field(multiple_of=multiple_of, ge=min_value)
        result = handle_constrained_float(
            random=Random(),
            multiple_of=constrained_field.multiple_of,
            gt=constrained_field.gt,
            ge=constrained_field.ge,
            lt=constrained_field.lt,
            le=constrained_field.le,
        )
        assert passes_pydantic_multiple_validator(result, multiple_of)
    else:
        with pytest.raises(ParameterError):
            constrained_field = create_constrained_field(multiple_of=multiple_of, ge=min_value)
            handle_constrained_float(
                random=Random(),
                multiple_of=constrained_field.multiple_of,
                gt=constrained_field.gt,
                ge=constrained_field.ge,
                lt=constrained_field.lt,
                le=constrained_field.le,
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
    ),
)
def test_handle_constrained_float_handles_multiple_of_with_gt(val1: float, val2: float) -> None:
    min_value, multiple_of = sorted([val1, val2])
    if multiple_of != 0.0:
        constrained_field = create_constrained_field(multiple_of=multiple_of, gt=min_value)
        result = handle_constrained_float(
            random=Random(),
            multiple_of=constrained_field.multiple_of,
            gt=constrained_field.gt,
            ge=constrained_field.ge,
            lt=constrained_field.lt,
            le=constrained_field.le,
        )
        assert passes_pydantic_multiple_validator(result, multiple_of)
    else:
        with pytest.raises(ParameterError):
            constrained_field = create_constrained_field(multiple_of=multiple_of, gt=min_value)
            handle_constrained_float(
                random=Random(),
                multiple_of=constrained_field.multiple_of,
                gt=constrained_field.gt,
                ge=constrained_field.ge,
                lt=constrained_field.lt,
                le=constrained_field.le,
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
    ),
    floats(
        allow_nan=False,
        allow_infinity=False,
        min_value=-1000000000,
        max_value=1000000000,
    ),
)
def test_handle_constrained_float_handles_multiple_of_with_ge_and_le(val1: float, val2: float, val3: float) -> None:
    min_value, multiple_of, max_value = sorted([val1, val2, val3])
    if multiple_of != 0.0 and is_multiply_of_multiple_of_in_range(
        minimum=min_value, maximum=max_value, multiple_of=multiple_of
    ):
        constrained_field = create_constrained_field(multiple_of=multiple_of, ge=min_value, le=max_value)
        result = handle_constrained_float(
            random=Random(),
            multiple_of=constrained_field.multiple_of,
            gt=constrained_field.gt,
            ge=constrained_field.ge,
            lt=constrained_field.lt,
            le=constrained_field.le,
        )
        assert passes_pydantic_multiple_validator(result, multiple_of)
    else:
        with pytest.raises(ParameterError):
            constrained_field = create_constrained_field(multiple_of=multiple_of, ge=min_value, le=max_value)
            handle_constrained_float(
                random=Random(),
                multiple_of=constrained_field.multiple_of,
                gt=constrained_field.gt,
                ge=constrained_field.ge,
                lt=constrained_field.lt,
                le=constrained_field.le,
            )
