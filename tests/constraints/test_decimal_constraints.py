from decimal import Decimal
from random import Random
from typing import Optional, cast

import pytest
from hypothesis import given
from hypothesis.strategies import decimals, integers

from pydantic import BaseModel, condecimal

from polyfactory.exceptions import ParameterException
from polyfactory.factories.pydantic_factory import ModelFactory
from polyfactory.value_generators.constrained_numbers import (
    handle_constrained_decimal,
    handle_decimal_length,
    is_multiply_of_multiple_of_in_range,
    passes_pydantic_multiple_validator,
)


def test_handle_constrained_decimal_without_constraints() -> None:
    result = handle_constrained_decimal(
        random=Random(),
        multiple_of=None,
        decimal_places=None,
        max_digits=None,
        gt=None,
        ge=None,
        lt=None,
        le=None,
    )
    assert isinstance(result, Decimal)


def test_handle_constrained_decimal_length_validation() -> None:
    with pytest.raises(ParameterException):
        handle_constrained_decimal(
            random=Random(),
            max_digits=2,
            ge=Decimal("100.000"),
        )


@given(integers(min_value=0, max_value=100))
def test_handle_constrained_decimal_handles_max_digits(max_digits: int) -> None:
    if max_digits > 0:
        result = handle_constrained_decimal(
            random=Random(),
            max_digits=max_digits,
        )
        assert len(result.as_tuple().digits) - abs(cast("int", result.as_tuple().exponent)) <= max_digits
    else:
        with pytest.raises(ParameterException):
            handle_constrained_decimal(
                random=Random(),
                max_digits=max_digits,
            )


@given(integers(min_value=0, max_value=100))
def test_handle_constrained_decimal_handles_decimal_places(decimal_places: int) -> None:
    result = handle_constrained_decimal(
        random=Random(),
        decimal_places=decimal_places,
    )
    assert abs(cast("int", result.as_tuple().exponent)) <= decimal_places


@given(integers(min_value=0, max_value=100), integers(min_value=1, max_value=100))
def test_handle_constrained_decimal_handles_max_digits_and_decimal_places(max_digits: int, decimal_places: int) -> None:
    if max_digits > 0 and max_digits > decimal_places:
        result = handle_constrained_decimal(
            random=Random(),
            decimal_places=decimal_places,
            max_digits=max_digits,
        )
        assert len(result.as_tuple().digits) - abs(cast("int", result.as_tuple().exponent)) <= max_digits
    else:
        with pytest.raises(ParameterException):
            handle_constrained_decimal(
                random=Random(),
                decimal_places=decimal_places,
                max_digits=max_digits,
            )


@given(
    decimals(
        allow_nan=False,
        allow_infinity=False,
        min_value=-1000000000,
        max_value=1000000000,
    ),
)
def test_handle_constrained_decimal_handles_ge(minimum: Decimal) -> None:
    result = handle_constrained_decimal(
        random=Random(),
        ge=minimum,
    )
    assert result >= minimum


@given(
    decimals(
        allow_nan=False,
        allow_infinity=False,
        min_value=-1000000000,
        max_value=1000000000,
    ),
)
def test_handle_constrained_decimal_handles_gt(minimum: Decimal) -> None:
    result = handle_constrained_decimal(
        random=Random(),
        gt=minimum,
    )
    assert result > minimum


@given(
    decimals(
        allow_nan=False,
        allow_infinity=False,
        min_value=-1000000000,
        max_value=1000000000,
    ),
)
def test_handle_constrained_decimal_handles_le(maximum: Decimal) -> None:
    result = handle_constrained_decimal(
        random=Random(),
        le=maximum,
    )
    assert result <= maximum


@given(
    decimals(
        allow_nan=False,
        allow_infinity=False,
        min_value=-1000000000,
        max_value=1000000000,
    ),
)
def test_handle_constrained_decimal_handles_lt(maximum: Decimal) -> None:
    result = handle_constrained_decimal(
        random=Random(),
        lt=maximum,
    )
    assert result < maximum


@given(
    decimals(
        allow_nan=False,
        allow_infinity=False,
        min_value=-1000000000,
        max_value=1000000000,
    ),
)
def test_handle_constrained_decimal_handles_multiple_of(multiple_of: Decimal) -> None:
    if multiple_of != Decimal("0"):
        result = handle_constrained_decimal(
            random=Random(),
            multiple_of=multiple_of,
        )
        assert passes_pydantic_multiple_validator(result, multiple_of)
    else:
        with pytest.raises(ParameterException):
            handle_constrained_decimal(
                random=Random(),
                multiple_of=multiple_of,
            )


@given(
    decimals(
        allow_nan=False,
        allow_infinity=False,
        min_value=-1000000000,
        max_value=1000000000,
    ),
    decimals(
        allow_nan=False,
        allow_infinity=False,
        min_value=-1000000000,
        max_value=1000000000,
    ),
)
def test_handle_constrained_decimal_handles_multiple_of_with_lt(val1: Decimal, val2: Decimal) -> None:
    multiple_of, max_value = sorted([val1, val2])
    if multiple_of != Decimal("0"):
        result = handle_constrained_decimal(
            random=Random(),
            multiple_of=multiple_of,
            lt=max_value,
        )
        assert passes_pydantic_multiple_validator(result, multiple_of)
    else:
        with pytest.raises(ParameterException):
            handle_constrained_decimal(
                random=Random(),
                multiple_of=multiple_of,
                lt=max_value,
            )


@given(
    decimals(
        allow_nan=False,
        allow_infinity=False,
        min_value=-1000000000,
        max_value=1000000000,
    ),
    decimals(
        allow_nan=False,
        allow_infinity=False,
        min_value=-1000000000,
        max_value=1000000000,
    ),
)
def test_handle_constrained_decimal_handles_multiple_of_with_le(val1: Decimal, val2: Decimal) -> None:
    multiple_of, max_value = sorted([val1, val2])
    if multiple_of != Decimal("0"):
        result = handle_constrained_decimal(
            random=Random(),
            multiple_of=multiple_of,
            le=max_value,
        )
        assert passes_pydantic_multiple_validator(result, multiple_of)
    else:
        with pytest.raises(ParameterException):
            handle_constrained_decimal(
                random=Random(),
                multiple_of=multiple_of,
                le=max_value,
            )


@given(
    decimals(
        allow_nan=False,
        allow_infinity=False,
        min_value=-1000000000,
        max_value=1000000000,
    ),
    decimals(
        allow_nan=False,
        allow_infinity=False,
        min_value=-1000000000,
        max_value=1000000000,
    ),
)
def test_handle_constrained_decimal_handles_multiple_of_with_ge(val1: Decimal, val2: Decimal) -> None:
    min_value, multiple_of = sorted([val1, val2])
    if multiple_of != Decimal("0"):
        result = handle_constrained_decimal(
            random=Random(),
            multiple_of=multiple_of,
            ge=min_value,
        )
        assert passes_pydantic_multiple_validator(result, multiple_of)
    else:
        with pytest.raises(ParameterException):
            handle_constrained_decimal(
                random=Random(),
                multiple_of=multiple_of,
                ge=min_value,
            )


@given(
    decimals(
        allow_nan=False,
        allow_infinity=False,
        min_value=-1000000000,
        max_value=1000000000,
    ),
    decimals(
        allow_nan=False,
        allow_infinity=False,
        min_value=-1000000000,
        max_value=1000000000,
    ),
)
def test_handle_constrained_decimal_handles_multiple_of_with_gt(val1: Decimal, val2: Decimal) -> None:
    min_value, multiple_of = sorted([val1, val2])
    if multiple_of != Decimal("0"):
        result = handle_constrained_decimal(
            random=Random(),
            multiple_of=multiple_of,
            gt=min_value,
        )
        assert passes_pydantic_multiple_validator(result, multiple_of)
    else:
        with pytest.raises(ParameterException):
            handle_constrained_decimal(
                random=Random(),
                multiple_of=multiple_of,
                gt=min_value,
            )


@given(
    decimals(
        allow_nan=False,
        allow_infinity=False,
        min_value=-1000000000,
        max_value=1000000000,
    ),
    decimals(
        allow_nan=False,
        allow_infinity=False,
        min_value=-1000000000,
        max_value=1000000000,
    ),
    decimals(
        allow_nan=False,
        allow_infinity=False,
        min_value=-1000000000,
        max_value=1000000000,
    ),
)
def test_handle_constrained_decimal_handles_multiple_of_with_ge_and_le(
    val1: Decimal,
    val2: Decimal,
    val3: Decimal,
) -> None:
    min_value, multiple_of, max_value = sorted([val1, val2, val3])
    if multiple_of != Decimal("0") and is_multiply_of_multiple_of_in_range(
        minimum=min_value,
        maximum=max_value,
        multiple_of=multiple_of,
    ):
        result = handle_constrained_decimal(
            random=Random(),
            multiple_of=multiple_of,
            ge=min_value,
            le=max_value,
        )
        assert passes_pydantic_multiple_validator(result, multiple_of)
    else:
        with pytest.raises(ParameterException):
            handle_constrained_decimal(
                random=Random(),
                multiple_of=multiple_of,
                ge=min_value,
                le=max_value,
            )


def test_max_digits_and_decimal_places() -> None:
    class Person(BaseModel):
        social_score: condecimal(
            decimal_places=4,
            max_digits=5,
            gt=Decimal("0.0"),
            le=Decimal("9.9999"),
        )  # type: ignore

    class PersonFactory(ModelFactory):
        __model__ = Person

    result = PersonFactory.build()
    assert isinstance(result.social_score, Decimal)
    assert len(str(result.social_score).split(".")[1]) == 4
    assert result.social_score > 0


def test_handle_decimal_length() -> None:
    decimal = Decimal("999.9999999")

    # here digits should determine decimal length
    max_digits = 5
    decimal_places: Optional[int] = 5

    result = handle_decimal_length(decimal, decimal_places, max_digits)

    assert isinstance(result, Decimal)
    assert len(result.as_tuple().digits) == 5
    assert abs(cast("int", result.as_tuple().exponent)) == 2

    # here decimal places should determine max length
    max_digits = 10
    decimal_places = 5

    result = handle_decimal_length(decimal, decimal_places, max_digits)
    assert isinstance(result, Decimal)
    assert len(result.as_tuple().digits) == 8
    assert abs(cast("int", result.as_tuple().exponent)) == 5

    # here digits determine decimal length
    max_digits = 10
    decimal_places = None

    result = handle_decimal_length(decimal, decimal_places, max_digits)
    assert isinstance(result, Decimal)
    assert len(result.as_tuple().digits) == 10
    assert abs(cast("int", result.as_tuple().exponent)) == 7

    # here decimal places determine decimal length
    max_digits = None  # type: ignore
    decimal_places = 5

    result = handle_decimal_length(decimal, decimal_places, max_digits)
    assert isinstance(result, Decimal)
    assert len(result.as_tuple().digits) == 8
    assert abs(cast("int", result.as_tuple().exponent)) == 5

    # here max_decimals is below 0
    decimal = Decimal("99.99")
    max_digits = 1
    result = handle_decimal_length(decimal, decimal_places, max_digits)
    assert isinstance(result, Decimal)
    assert len(result.as_tuple().digits) == 1
    assert cast("int", result.as_tuple().exponent) == 0


def test_zero_to_one_range() -> None:
    class FractionExample(BaseModel):
        fraction: condecimal(ge=Decimal("0.0"), le=Decimal("1.0"), decimal_places=2, max_digits=3)  # type: ignore

    class FractionExampleFactory(ModelFactory):
        __model__ = FractionExample

    result = FractionExampleFactory.build()

    assert result.fraction >= Decimal("0")
    assert result.fraction <= Decimal("1")
