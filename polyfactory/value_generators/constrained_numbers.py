from decimal import Decimal
from sys import float_info
from typing import TYPE_CHECKING, Any, Dict, Optional, Tuple, Type, TypeVar, cast

from polyfactory.exceptions import ParameterError
from polyfactory.value_generators.primitives import (
    create_random_decimal,
    create_random_float,
    create_random_integer,
)

if TYPE_CHECKING:
    from random import Random

    from polyfactory.protocols import NumberGeneratorProtocol

T = TypeVar("T", Decimal, int, float)


def almost_equal_floats(value_1: float, value_2: float, *, delta: float = 1e-8) -> bool:
    """Return True if two floats are almost equal

    Note: this utility is ported from pydantic
    """
    return abs(value_1 - value_2) <= delta


def is_multiply_of_multiple_of_in_range(
    minimum: T,
    maximum: T,
    multiple_of: T,
) -> bool:
    """Determines if at least one multiply of `multiple_of` lies in the given range."""
    # if the range has infinity on one of its ends then infinite number of multipliers
    # can be found within the range

    # if we were given floats and multiple_of is really close to zero then it doesn't make sense
    # to continue trying to check the range
    if (
        isinstance(minimum, float)
        and isinstance(multiple_of, float)
        and minimum / multiple_of in [float("+inf"), float("-inf")]
    ):
        return False

    multiplier = round(minimum / multiple_of)
    step = 1 if multiple_of > 0 else -1
    # since rounding can go either up or down we may end up in a situation when
    # minimum is less or equal to `multiplier * multiple_of`
    # or when it is greater than `multiplier * multiple_of`
    # (in this case minimum is less than `(multiplier + 1)* multiple_of`). So we need to check
    # that any of two values is inside the given range. ASCII graphic below explain this
    #
    #                minimum
    # -----------------+-------+-----------------------------------+----------------------------
    #             multiplier * multiple_of        (multiplier + 1) * multiple_of
    #
    #
    #                                minimum
    # -------------------------+--------+--------------------------+----------------------------
    #             multiplier * multiple_of        (multiplier + 1) * multiple_of
    #
    # since `multiple_of` can be a negative number adding +1 to `multiplier` drives `(multiplier + 1) * multiple_of``
    # away from `minimum` to the -infinity. It looks like this:
    #                                                                               minimum
    # -----------------------+--------------------------------+------------------------+--------
    #       (multiplier + 1) * multiple_of        (multiplier) * multiple_of
    #
    # so for negative `multiple_of` we want to subtract 1 from multiplier
    for multiply in [multiplier * multiple_of, (multiplier + step) * multiple_of]:
        multiply_float = float(multiply)
        if (
            almost_equal_floats(multiply_float, float(minimum))
            or almost_equal_floats(multiply_float, float(maximum))
            or minimum < multiply < maximum
        ):
            return True

    return False


def passes_pydantic_multiple_validator(value: T, multiple_of: T) -> bool:
    """A function that determines whether a given value passes the pydantic multiple_of validation."""
    if multiple_of == 0:
        return True
    mod = float(value) / float(multiple_of) % 1
    return almost_equal_floats(mod, 0.0) or almost_equal_floats(mod, 1.0)


def get_increment(t_type: Type[T]) -> T:
    """Gets a small increment base to add to constrained values, i.e. lt/gt entries.

    Args:
        t_type: A value of type T.

    Returns:
        An increment T.
    """
    values: Dict[Any, Any] = {int: 1, float: float_info.epsilon, Decimal: Decimal("0.001")}
    return cast("T", values[t_type])


def get_value_or_none(equal_value: Optional[T], constrained: Optional[T], increment: T) -> Optional[T]:
    """helper function to reduce branching in the get_constrained_number_range method if the ge/le value is available,
    return that, otherwise return the gt/lt value + an increment or None.

    Args:
        equal_value: An GE/LE value.
        constrained: An GT/LT value.
        increment: increment.

    Returns:
        Optional T.
    """
    if equal_value is not None:
        return equal_value
    if constrained is not None:
        return constrained + increment
    return None


def get_constrained_number_range(
    t_type: Type[T],
    random: "Random",
    lt: Optional[T] = None,
    le: Optional[T] = None,
    gt: Optional[T] = None,
    ge: Optional[T] = None,
    multiple_of: Optional[T] = None,
) -> Tuple[Optional[T], Optional[T]]:
    """Returns the minimum and maximum values given a field_meta's constraints."""
    seed = t_type(random.random() * 10)
    minimum = get_value_or_none(equal_value=ge, constrained=gt, increment=get_increment(t_type))
    maximum = get_value_or_none(equal_value=le, constrained=lt, increment=-get_increment(t_type))  # pyright: ignore

    if minimum is not None and maximum is not None and maximum < minimum:
        raise ParameterError("maximum value must be greater than minimum value")

    if multiple_of is None:
        if minimum is not None and maximum is None:
            if minimum == 0:
                return minimum, seed  # pyright: ignore
            return minimum, minimum + seed
        if maximum is not None and minimum is None:
            return maximum - seed, maximum
    else:
        if multiple_of == 0.0:
            raise ParameterError("multiple_of can not be zero")
        if (
            minimum is not None
            and maximum is not None
            and not is_multiply_of_multiple_of_in_range(minimum=minimum, maximum=maximum, multiple_of=multiple_of)
        ):
            raise ParameterError("given range should include at least one multiply of multiple_of")

    return minimum, maximum


def generate_constrained_number(
    random: "Random",
    minimum: Optional[T],
    maximum: Optional[T],
    multiple_of: Optional[T],
    method: "NumberGeneratorProtocol[T]",
) -> T:
    """Generate a constrained number, output depends on the passed in callbacks.

    :param random:
    :param minimum:
    :param maximum:
    :param multiple_of:
    :param method:
    :return:
    """
    if minimum is not None and maximum is not None:
        if multiple_of is None:
            return method(random=random, minimum=minimum, maximum=maximum)
        if multiple_of >= minimum:
            return multiple_of
        result = minimum
        while not passes_pydantic_multiple_validator(result, multiple_of):
            result = round(method(random=random, minimum=minimum, maximum=maximum) / multiple_of) * multiple_of
        return result
    if multiple_of is not None:
        return multiple_of
    return method(random=random)


def handle_constrained_int(
    random: "Random",
    multiple_of: Optional[int] = None,
    gt: Optional[int] = None,
    ge: Optional[int] = None,
    lt: Optional[int] = None,
    le: Optional[int] = None,
) -> int:
    """Handles 'ConstrainedInt' instances."""

    minimum, maximum = get_constrained_number_range(
        gt=gt, ge=ge, lt=lt, le=le, t_type=int, multiple_of=multiple_of, random=random
    )
    return generate_constrained_number(
        random=random, minimum=minimum, maximum=maximum, multiple_of=multiple_of, method=create_random_integer
    )


def handle_constrained_float(
    random: "Random",
    multiple_of: Optional[float] = None,
    gt: Optional[float] = None,
    ge: Optional[float] = None,
    lt: Optional[float] = None,
    le: Optional[float] = None,
) -> float:
    """
    :param random:
    :param multiple_of:
    :param gt:
    :param ge:
    :param lt:
    :param le:
    :return:
    """

    minimum, maximum = get_constrained_number_range(
        gt=gt, ge=ge, lt=lt, le=le, t_type=float, multiple_of=multiple_of, random=random
    )

    return generate_constrained_number(
        random=random,
        minimum=minimum,
        maximum=maximum,
        multiple_of=multiple_of,
        method=create_random_float,
    )


def validate_max_digits(
    max_digits: int,
    minimum: Optional[Decimal],
    decimal_places: Optional[int],
) -> None:
    """Validates that max digits is greater than minimum and decimal places.

    Args:
        max_digits: The maximal number of digits for the decimal.
        minimum: Minimal value.
        decimal_places: Number of decimal places

    Returns:
        'None'
    """
    if max_digits <= 0:
        raise ParameterError("max_digits must be greater than 0")

    if minimum is not None:
        min_str = str(minimum).split(".")[1] if "." in str(minimum) else str(minimum)

        if max_digits <= len(min_str):
            raise ParameterError("minimum is greater than max_digits")

    if decimal_places is not None and max_digits <= decimal_places:
        raise ParameterError("max_digits must be greater than decimal places")


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


def handle_constrained_decimal(
    random: "Random",
    multiple_of: Optional[Decimal] = None,
    decimal_places: Optional[int] = None,
    max_digits: Optional[int] = None,
    gt: Optional[Decimal] = None,
    ge: Optional[Decimal] = None,
    lt: Optional[Decimal] = None,
    le: Optional[Decimal] = None,
) -> Decimal:
    """
    :param random:
    :param multiple_of:
    :param decimal_places:
    :param max_digits:
    :param gt:
    :param ge:
    :param lt:
    :param le:
    :return:
    """

    minimum, maximum = get_constrained_number_range(
        gt=gt, ge=ge, lt=lt, le=le, multiple_of=multiple_of, t_type=Decimal, random=random
    )

    if max_digits is not None:
        validate_max_digits(max_digits=max_digits, minimum=minimum, decimal_places=decimal_places)

    generated_decimal = generate_constrained_number(
        random=random,
        minimum=minimum,
        maximum=maximum,
        multiple_of=multiple_of,
        method=create_random_decimal,
    )

    if max_digits is not None or decimal_places is not None:
        return handle_decimal_length(
            generated_decimal=generated_decimal, max_digits=max_digits, decimal_places=decimal_places
        )

    return generated_decimal
