from decimal import Decimal
from typing import TYPE_CHECKING, Optional, cast

from pydantic_factories.value_generators.constrained_number import (
    generate_constrained_number,
    get_constrained_number_range,
)
from pydantic_factories.value_generators.primitives import create_random_decimal

if TYPE_CHECKING:
    from pydantic import ConstrainedDecimal


def validate_max_digits(
    max_digits: int,
    minimum: Optional[Decimal],
    decimal_places: Optional[int],
) -> None:
    """Validates that max digits and other parameters make sense."""
    assert max_digits > 0, "max_digits must be greater than 0"
    if minimum is not None:
        min_str = str(minimum).split(".")[1] if "." in str(minimum) else str(minimum)
        assert max_digits >= len(min_str), "minimum is greater than max_digits"
    if decimal_places is not None:
        assert max_digits >= decimal_places, "max_digits must be greater than decimal places"


def handle_decimal_length(
    generated_decimal: Decimal,
    decimal_places: Optional[int],
    max_digits: Optional[int],
) -> Decimal:
    """Handles the length of the decimal."""
    string_number = str(generated_decimal)
    sign = "-" if "-" in string_number else "+"
    string_number = string_number.replace("-", "")
    whole_numbers, decimals = string_number.split(".")

    if max_digits is not None and decimal_places is not None:
        if len(whole_numbers) + decimal_places > max_digits:
            # max digits determines decimal length
            max_decimals = max_digits - len(whole_numbers)
        else:
            # decimal places determines max decimal length
            max_decimals = decimal_places
    elif max_digits is not None:
        max_decimals = max_digits - len(whole_numbers)
    else:
        max_decimals = cast("int", decimal_places)

    if max_decimals < 0:
        # in this case there are fewer digits than the len of whole_numbers
        return Decimal(sign + whole_numbers[:max_decimals])

    decimals = decimals[:max_decimals]
    return Decimal(sign + whole_numbers + "." + decimals[:decimal_places])


def handle_constrained_decimal(field: "ConstrainedDecimal") -> Decimal:
    """Handles 'ConstrainedDecimal' instances."""
    multiple_of = cast("Optional[Decimal]", field.multiple_of)
    decimal_places = field.decimal_places
    max_digits = field.max_digits
    if multiple_of == 0:
        return Decimal(0)
    minimum, maximum = get_constrained_number_range(
        gt=field.gt, ge=field.ge, lt=field.lt, le=field.le, multiple_of=multiple_of, t_type=Decimal  # type: ignore
    )
    if max_digits is not None:
        validate_max_digits(max_digits=max_digits, minimum=cast("Decimal", minimum), decimal_places=decimal_places)
    generated_decimal = generate_constrained_number(
        minimum=cast("Decimal", minimum),
        maximum=cast("Decimal", maximum),
        multiple_of=multiple_of,
        method=create_random_decimal,
    )
    if max_digits is not None or decimal_places is not None:
        return handle_decimal_length(
            generated_decimal=generated_decimal, max_digits=max_digits, decimal_places=decimal_places
        )
    return generated_decimal
