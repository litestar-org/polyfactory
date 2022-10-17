import random
from decimal import Decimal
from typing import Any, Callable, Dict, Optional, Tuple, Type, TypeVar, cast

from pydantic_factories.exceptions import ParameterError
from pydantic_factories.utils import passes_pydantic_multiple_validator

T = TypeVar("T", Decimal, int, float)


def get_increment(t_type: Type[T]) -> T:
    """Gets a small increment base to add to constrained values, i.e. lt/gt
    entries.

    Args:
        t_type: A value of type T.

    Returns:
        An increment T.
    """
    values: Dict[Any, Any] = {int: 1, float: 0.001, Decimal: Decimal("0.001")}
    return cast("T", values[t_type])


def get_value_or_none(equal_value: Optional[T], constrained: Optional[T], increment: T) -> Optional[T]:
    """helper function to reduce branching in the get_constrained_number_range
    method if the ge/le value is available, return that, otherwise return the
    gt/lt value + an increment or None.

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
    lt: Optional[T],
    le: Optional[T],
    gt: Optional[T],
    ge: Optional[T],
    t_type: Type[T],
    multiple_of: Optional[T] = None,
) -> Tuple[Optional[T], Optional[T]]:
    """Returns the minimum and maximum values given a field's constraints."""
    seed = t_type(random.random() * 10)
    minimum = get_value_or_none(equal_value=ge, constrained=gt, increment=get_increment(t_type))
    maximum = get_value_or_none(equal_value=le, constrained=lt, increment=-get_increment(t_type))  # pyright: ignore

    if minimum is not None and maximum is not None and maximum <= minimum:
        raise ParameterError("maximum value must be greater than minimum value")

    if multiple_of is None:
        if minimum is not None and maximum is None:
            if minimum == 0:
                return minimum, seed
            return minimum, minimum + seed
        if maximum is not None and minimum is None:
            return maximum - seed, maximum
    elif maximum is not None and multiple_of >= maximum:
        raise ParameterError("maximum value must be greater than multiple_of")

    return minimum, maximum


def generate_constrained_number(
    minimum: Optional[T],
    maximum: Optional[T],
    multiple_of: Optional[T],
    method: Callable,
) -> T:
    """Generates a constrained number, output depends on the passed in
    callbacks."""
    if minimum is not None and maximum is not None:
        if multiple_of is None:
            return cast("T", method(minimum, maximum))
        if multiple_of >= minimum:
            return multiple_of
        result = minimum
        while not passes_pydantic_multiple_validator(result, multiple_of):
            result = round(method(minimum, maximum) / multiple_of) * multiple_of
        return result
    if multiple_of is not None:
        return multiple_of
    return cast("T", method())
