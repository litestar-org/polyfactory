from random import Random
from typing import Optional

import pytest
from hypothesis import given
from hypothesis.strategies import integers
from pydantic import ConstrainedInt

from polyfactory.exceptions import ParameterException
from polyfactory.value_generators.constrained_numbers import (
    handle_constrained_int,
    is_multiply_of_multiple_of_in_range,
    passes_pydantic_multiple_validator,
)


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
    constrained_field = create_constrained_field()
    result = handle_constrained_int(
        random=Random(),
        multiple_of=constrained_field.multiple_of,
        gt=constrained_field.gt,
        ge=constrained_field.ge,
        lt=constrained_field.lt,
        le=constrained_field.le,
    )
    assert isinstance(result, int)


@given(integers(min_value=-1000000000, max_value=1000000000))
def test_handle_constrained_int_handles_ge(minimum: int) -> None:
    constrained_field = create_constrained_field(ge=minimum)
    result = handle_constrained_int(
        random=Random(),
        multiple_of=constrained_field.multiple_of,
        gt=constrained_field.gt,
        ge=constrained_field.ge,
        lt=constrained_field.lt,
        le=constrained_field.le,
    )
    assert result >= minimum


@given(integers(min_value=-1000000000, max_value=1000000000))
def test_handle_constrained_int_handles_gt(minimum: int) -> None:
    constrained_field = create_constrained_field(gt=minimum)
    result = handle_constrained_int(
        random=Random(),
        multiple_of=constrained_field.multiple_of,
        gt=constrained_field.gt,
        ge=constrained_field.ge,
        lt=constrained_field.lt,
        le=constrained_field.le,
    )
    assert result > minimum


@given(integers(min_value=-1000000000, max_value=1000000000))
def test_handle_constrained_int_handles_le(maximum: int) -> None:
    constrained_field = create_constrained_field(le=maximum)
    result = handle_constrained_int(
        random=Random(),
        multiple_of=constrained_field.multiple_of,
        gt=constrained_field.gt,
        ge=constrained_field.ge,
        lt=constrained_field.lt,
        le=constrained_field.le,
    )
    assert result <= maximum


@given(integers(min_value=-1000000000, max_value=1000000000))
def test_handle_constrained_int_handles_lt(maximum: int) -> None:
    constrained_field = create_constrained_field(lt=maximum)
    result = handle_constrained_int(
        random=Random(),
        multiple_of=constrained_field.multiple_of,
        gt=constrained_field.gt,
        ge=constrained_field.ge,
        lt=constrained_field.lt,
        le=constrained_field.le,
    )
    assert result < maximum


@given(integers(min_value=-1000000000, max_value=1000000000))
def test_handle_constrained_int_handles_multiple_of(multiple_of: int) -> None:
    if multiple_of != 0:
        constrained_field = create_constrained_field(multiple_of=multiple_of)
        result = handle_constrained_int(
            random=Random(),
            multiple_of=constrained_field.multiple_of,
            gt=constrained_field.gt,
            ge=constrained_field.ge,
            lt=constrained_field.lt,
            le=constrained_field.le,
        )
        assert passes_pydantic_multiple_validator(result, multiple_of)
    else:
        with pytest.raises(ParameterException):
            constrained_field = create_constrained_field(multiple_of=multiple_of)
            handle_constrained_int(
                random=Random(),
                multiple_of=constrained_field.multiple_of,
                gt=constrained_field.gt,
                ge=constrained_field.ge,
                lt=constrained_field.lt,
                le=constrained_field.le,
            )


@given(
    integers(min_value=-1000000000, max_value=1000000000),
    integers(min_value=-1000000000, max_value=1000000000),
)
def test_handle_constrained_int_handles_multiple_of_with_lt(val1: int, val2: int) -> None:
    multiple_of, max_value = sorted([val1, val2])
    if multiple_of != 0:
        constrained_field = create_constrained_field(multiple_of=multiple_of, lt=max_value)
        result = handle_constrained_int(
            random=Random(),
            multiple_of=constrained_field.multiple_of,
            gt=constrained_field.gt,
            ge=constrained_field.ge,
            lt=constrained_field.lt,
            le=constrained_field.le,
        )
        assert passes_pydantic_multiple_validator(result, multiple_of)
    else:
        with pytest.raises(ParameterException):
            constrained_field = create_constrained_field(multiple_of=multiple_of, lt=max_value)
            handle_constrained_int(
                random=Random(),
                multiple_of=constrained_field.multiple_of,
                gt=constrained_field.gt,
                ge=constrained_field.ge,
                lt=constrained_field.lt,
                le=constrained_field.le,
            )


@given(
    integers(min_value=-1000000000, max_value=1000000000),
    integers(min_value=-1000000000, max_value=1000000000),
)
def test_handle_constrained_int_handles_multiple_of_with_le(val1: int, val2: int) -> None:
    multiple_of, max_value = sorted([val1, val2])
    if multiple_of != 0:
        constrained_field = create_constrained_field(multiple_of=multiple_of, le=max_value)
        result = handle_constrained_int(
            random=Random(),
            multiple_of=constrained_field.multiple_of,
            gt=constrained_field.gt,
            ge=constrained_field.ge,
            lt=constrained_field.lt,
            le=constrained_field.le,
        )
        assert passes_pydantic_multiple_validator(result, multiple_of)
    else:
        with pytest.raises(ParameterException):
            constrained_field = create_constrained_field(multiple_of=multiple_of, le=max_value)
            handle_constrained_int(
                random=Random(),
                multiple_of=constrained_field.multiple_of,
                gt=constrained_field.gt,
                ge=constrained_field.ge,
                lt=constrained_field.lt,
                le=constrained_field.le,
            )


@given(
    integers(min_value=-1000000000, max_value=1000000000),
    integers(min_value=-1000000000, max_value=1000000000),
)
def test_handle_constrained_int_handles_multiple_of_with_ge(val1: int, val2: int) -> None:
    min_value, multiple_of = sorted([val1, val2])
    if multiple_of != 0:
        constrained_field = create_constrained_field(multiple_of=multiple_of, ge=min_value)
        result = handle_constrained_int(
            random=Random(),
            multiple_of=constrained_field.multiple_of,
            gt=constrained_field.gt,
            ge=constrained_field.ge,
            lt=constrained_field.lt,
            le=constrained_field.le,
        )
        assert passes_pydantic_multiple_validator(result, multiple_of)
    else:
        with pytest.raises(ParameterException):
            constrained_field = create_constrained_field(multiple_of=multiple_of, ge=min_value)
            handle_constrained_int(
                random=Random(),
                multiple_of=constrained_field.multiple_of,
                gt=constrained_field.gt,
                ge=constrained_field.ge,
                lt=constrained_field.lt,
                le=constrained_field.le,
            )


@given(
    integers(min_value=-1000000000, max_value=1000000000),
    integers(min_value=-1000000000, max_value=1000000000),
)
def test_handle_constrained_int_handles_multiple_of_with_gt(val1: int, val2: int) -> None:
    min_value, multiple_of = sorted([val1, val2])
    if multiple_of != 0:
        constrained_field = create_constrained_field(multiple_of=multiple_of, gt=min_value)
        result = handle_constrained_int(
            random=Random(),
            multiple_of=constrained_field.multiple_of,
            gt=constrained_field.gt,
            ge=constrained_field.ge,
            lt=constrained_field.lt,
            le=constrained_field.le,
        )
        assert passes_pydantic_multiple_validator(result, multiple_of)
    else:
        with pytest.raises(ParameterException):
            constrained_field = create_constrained_field(multiple_of=multiple_of, gt=min_value)
            handle_constrained_int(
                random=Random(),
                multiple_of=constrained_field.multiple_of,
                gt=constrained_field.gt,
                ge=constrained_field.ge,
                lt=constrained_field.lt,
                le=constrained_field.le,
            )


@given(
    integers(min_value=-1000000000, max_value=1000000000),
    integers(min_value=-1000000000, max_value=1000000000),
    integers(min_value=-1000000000, max_value=1000000000),
)
def test_handle_constrained_int_handles_multiple_of_with_ge_and_le(val1: int, val2: int, val3: int) -> None:
    min_value, multiple_of, max_value = sorted([val1, val2, val3])
    if multiple_of != 0 and is_multiply_of_multiple_of_in_range(
        minimum=min_value, maximum=max_value, multiple_of=multiple_of
    ):
        constrained_field = create_constrained_field(multiple_of=multiple_of, ge=min_value, le=max_value)
        result = handle_constrained_int(
            random=Random(),
            multiple_of=constrained_field.multiple_of,
            gt=constrained_field.gt,
            ge=constrained_field.ge,
            lt=constrained_field.lt,
            le=constrained_field.le,
        )
        assert passes_pydantic_multiple_validator(result, multiple_of)
    else:
        with pytest.raises(ParameterException):
            constrained_field = create_constrained_field(multiple_of=multiple_of, ge=min_value, le=max_value)
            handle_constrained_int(
                random=Random(),
                multiple_of=constrained_field.multiple_of,
                gt=constrained_field.gt,
                ge=constrained_field.ge,
                lt=constrained_field.lt,
                le=constrained_field.le,
            )


def test_constraint_bounds_handling() -> None:
    constrained_field = create_constrained_field(ge=100, le=100)
    result = handle_constrained_int(
        random=Random(),
        multiple_of=constrained_field.multiple_of,
        gt=constrained_field.gt,
        ge=constrained_field.ge,
        lt=constrained_field.lt,
        le=constrained_field.le,
    )
    assert result == 100

    constrained_field = create_constrained_field(gt=100, lt=102)
    result = handle_constrained_int(
        random=Random(),
        multiple_of=constrained_field.multiple_of,
        gt=constrained_field.gt,
        ge=constrained_field.ge,
        lt=constrained_field.lt,
        le=constrained_field.le,
    )
    assert result == 101

    constrained_field = create_constrained_field(gt=100, le=101)
    result = handle_constrained_int(
        random=Random(),
        multiple_of=constrained_field.multiple_of,
        gt=constrained_field.gt,
        ge=constrained_field.ge,
        lt=constrained_field.lt,
        le=constrained_field.le,
    )
    assert result == 101

    with pytest.raises(ParameterException):
        constrained_field = create_constrained_field(gt=100, lt=101)
        result = handle_constrained_int(
            random=Random(),
            multiple_of=constrained_field.multiple_of,
            gt=constrained_field.gt,
            ge=constrained_field.ge,
            lt=constrained_field.lt,
            le=constrained_field.le,
        )

    with pytest.raises(ParameterException):
        constrained_field = create_constrained_field(ge=100, le=99)
        result = handle_constrained_int(
            random=Random(),
            multiple_of=constrained_field.multiple_of,
            gt=constrained_field.gt,
            ge=constrained_field.ge,
            lt=constrained_field.lt,
            le=constrained_field.le,
        )
