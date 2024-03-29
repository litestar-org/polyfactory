from random import Random

import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis.strategies import integers

from polyfactory.exceptions import ParameterException
from polyfactory.value_generators.constrained_numbers import (
    handle_constrained_int,
    is_multiply_of_multiple_of_in_range,
    passes_pydantic_multiple_validator,
)


def test_handle_constrained_int_without_constraints() -> None:
    result = handle_constrained_int(
        random=Random(),
    )
    assert isinstance(result, int)


@given(integers(min_value=-1000000000, max_value=1000000000))
def test_handle_constrained_int_handles_ge(minimum: int) -> None:
    result = handle_constrained_int(
        random=Random(),
        ge=minimum,
    )
    assert result >= minimum


@given(integers(min_value=-1000000000, max_value=1000000000))
def test_handle_constrained_int_handles_gt(minimum: int) -> None:
    result = handle_constrained_int(
        random=Random(),
        gt=minimum,
    )
    assert result > minimum


@given(integers(min_value=-1000000000, max_value=1000000000))
def test_handle_constrained_int_handles_le(maximum: int) -> None:
    result = handle_constrained_int(
        random=Random(),
        le=maximum,
    )
    assert result <= maximum


@given(integers(min_value=-1000000000, max_value=1000000000))
def test_handle_constrained_int_handles_lt(maximum: int) -> None:
    result = handle_constrained_int(
        random=Random(),
        lt=maximum,
    )
    assert result < maximum


@settings(suppress_health_check=(HealthCheck.filter_too_much,))
@given(
    integers(min_value=1, max_value=10),
    integers(min_value=1, max_value=10),
)
def test_handle_constrained_int_handles_ge_with_le(val1: int, val2: int) -> None:
    min_value, max_value = sorted([val1, val2])
    result = handle_constrained_int(
        random=Random(),
        ge=min_value,
        le=max_value,
    )
    assert min_value <= result <= max_value


@given(integers(min_value=-1000000000, max_value=1000000000))
def test_handle_constrained_int_handles_multiple_of(multiple_of: int) -> None:
    if multiple_of != 0:
        result = handle_constrained_int(
            random=Random(),
            multiple_of=multiple_of,
        )
        assert passes_pydantic_multiple_validator(result, multiple_of)
    else:
        with pytest.raises(ParameterException):
            handle_constrained_int(
                random=Random(),
                multiple_of=multiple_of,
            )


@given(
    integers(min_value=-1000000000, max_value=1000000000),
    integers(min_value=-1000000000, max_value=1000000000),
)
def test_handle_constrained_int_handles_multiple_of_with_lt(val1: int, val2: int) -> None:
    multiple_of, max_value = sorted([val1, val2])
    if multiple_of != 0:
        result = handle_constrained_int(
            random=Random(),
            multiple_of=multiple_of,
            lt=max_value,
        )
        assert passes_pydantic_multiple_validator(result, multiple_of)
    else:
        with pytest.raises(ParameterException):
            handle_constrained_int(
                random=Random(),
                multiple_of=multiple_of,
                lt=max_value,
            )


@given(
    integers(min_value=-1000000000, max_value=1000000000),
    integers(min_value=-1000000000, max_value=1000000000),
)
def test_handle_constrained_int_handles_multiple_of_with_le(val1: int, val2: int) -> None:
    multiple_of, max_value = sorted([val1, val2])
    if multiple_of != 0:
        result = handle_constrained_int(
            random=Random(),
            multiple_of=multiple_of,
            le=max_value,
        )
        assert passes_pydantic_multiple_validator(result, multiple_of)
    else:
        with pytest.raises(ParameterException):
            handle_constrained_int(
                random=Random(),
                multiple_of=multiple_of,
                le=max_value,
            )


@given(
    integers(min_value=-1000000000, max_value=1000000000),
    integers(min_value=-1000000000, max_value=1000000000),
)
def test_handle_constrained_int_handles_multiple_of_with_ge(val1: int, val2: int) -> None:
    min_value, multiple_of = sorted([val1, val2])
    if multiple_of != 0:
        result = handle_constrained_int(
            random=Random(),
            multiple_of=multiple_of,
            ge=min_value,
        )
        assert passes_pydantic_multiple_validator(result, multiple_of)
    else:
        with pytest.raises(ParameterException):
            handle_constrained_int(
                random=Random(),
                multiple_of=multiple_of,
                ge=min_value,
            )


@given(
    integers(min_value=-1000000000, max_value=1000000000),
    integers(min_value=-1000000000, max_value=1000000000),
)
def test_handle_constrained_int_handles_multiple_of_with_gt(val1: int, val2: int) -> None:
    min_value, multiple_of = sorted([val1, val2])
    if multiple_of != 0:
        result = handle_constrained_int(
            random=Random(),
            multiple_of=multiple_of,
            gt=min_value,
        )
        assert passes_pydantic_multiple_validator(result, multiple_of)
    else:
        with pytest.raises(ParameterException):
            handle_constrained_int(
                random=Random(),
                multiple_of=multiple_of,
                gt=min_value,
            )


@given(
    integers(min_value=-1000000000, max_value=1000000000),
    integers(min_value=-1000000000, max_value=1000000000),
    integers(min_value=-1000000000, max_value=1000000000),
)
def test_handle_constrained_int_handles_multiple_of_with_ge_and_le(val1: int, val2: int, val3: int) -> None:
    min_value, multiple_of, max_value = sorted([val1, val2, val3])
    if multiple_of != 0 and is_multiply_of_multiple_of_in_range(
        minimum=min_value,
        maximum=max_value,
        multiple_of=multiple_of,
    ):
        result = handle_constrained_int(
            random=Random(),
            multiple_of=multiple_of,
            ge=min_value,
            le=max_value,
        )
        assert passes_pydantic_multiple_validator(result, multiple_of)
    else:
        with pytest.raises(ParameterException):
            handle_constrained_int(
                random=Random(),
                multiple_of=multiple_of,
                ge=min_value,
                le=max_value,
            )


def test_constraint_randomness() -> None:
    random = Random(10)
    result = handle_constrained_int(
        random=random,
    )
    assert result == 55

    result = handle_constrained_int(
        random=random,
    )
    assert result == 61

    result = handle_constrained_int(
        random=random,
    )
    assert result == 85
