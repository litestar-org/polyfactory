from decimal import Decimal
from typing import Optional, cast

from pydantic import ConstrainedDecimal

from pydantic_factories.value_generators.constrained_number import (
    generate_constrained_number,
    get_constrained_number_range,
    get_increment,
)
from pydantic_factories.value_generators.primitives import create_random_decimal


def validate_max_digits(
    max_digits: int,
    minimum: Optional[Decimal],
    decimal_places: Optional[int],
) -> None:
    """Validates that max digits and other parameters make sense"""
    assert max_digits > 0, "max_digits must be greater than 0"
    if minimum is not None:
        minimum -= get_increment(Decimal)
        assert max_digits >= len(str(abs(minimum))), "minimum is greater than max_digits"
    if decimal_places is not None:
        assert max_digits > decimal_places, "max_digits must be greater than decimal places"


def handle_decimal_length(
    generated_decimal: Decimal,
    decimal_places: Optional[int],
    max_digits: Optional[int],
) -> Decimal:
    """
    Handles the length of the decimal
    """
    string_number = str(generated_decimal)
    sign = "-" if "-" in string_number else "+"
    string_number = string_number.replace("-", "")
    whole_numbers, decimals = string_number.split(".")
    if max_digits is not None and decimal_places is not None:
        max_length = max_digits - decimal_places
    elif max_digits is not None:
        max_length = max_digits
    else:
        max_length = cast(int, decimal_places)
    while len(whole_numbers) + len(decimals) > max_length:
        if max_digits is not None and decimal_places is None and len(whole_numbers) > 0:
            whole_numbers = whole_numbers[1:]
        elif len(decimals) > 0:
            decimals = decimals[: len(decimals) - 1]
        else:
            whole_numbers = whole_numbers[1:]
    return Decimal(f"{sign}{whole_numbers}" + (f".{decimals[:decimal_places]}" if decimals else "0"))


def handle_constrained_decimal(field: ConstrainedDecimal) -> Decimal:
    """
    Handles 'ConstrainedDecimal' instances
    """
    multiple_of = cast(Optional[Decimal], field.multiple_of)
    decimal_places = field.decimal_places
    max_digits = field.max_digits
    if multiple_of == 0:
        return Decimal(0)
    minimum, maximum = get_constrained_number_range(
        gt=field.gt, ge=field.ge, lt=field.lt, le=field.le, multiple_of=multiple_of, t_type=Decimal  # type: ignore
    )
    if max_digits is not None:
        validate_max_digits(max_digits=max_digits, minimum=cast(Decimal, minimum), decimal_places=decimal_places)
    generated_decimal = generate_constrained_number(
        minimum=cast(Decimal, minimum),
        maximum=cast(Decimal, maximum),
        multiple_of=multiple_of,
        method=create_random_decimal,
    )
    if max_digits is not None or decimal_places is not None:
        return handle_decimal_length(
            generated_decimal=generated_decimal, max_digits=max_digits, decimal_places=decimal_places
        )
    return generated_decimal
