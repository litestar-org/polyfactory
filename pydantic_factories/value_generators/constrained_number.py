from decimal import Decimal
from typing import Callable, Optional, Tuple, TypeVar, cast

from typing_extensions import Type

from pydantic_factories.utils import passes_pydantic_multiple_validator, random

T = TypeVar("T", Decimal, int, float)


def get_increment(t_type: Type[T]) -> T:
    """gets a small increment base to add to constrained values, i.e. lt/gt entries"""
    if t_type == int:
        return t_type(1)
    if t_type == float:
        return t_type(0.001)
    return t_type("0.001")


def get_value_or_none(equal_value: Optional[T], constrained: Optional[T], increment: T) -> Optional[T]:
    """
    helper function to reduce branching in the get_constrained_number_range method
    if the ge/le value is available, return that, otherwise return the gt/lt value + an increment or None
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
    """Returns the minimum and maximum values given a field's constraints"""
    seed = t_type(random.random() * 10)
    minimum = get_value_or_none(equal_value=ge, constrained=gt, increment=get_increment(t_type))
    maximum = get_value_or_none(equal_value=le, constrained=lt, increment=-get_increment(t_type))
    if minimum is not None and maximum is not None:
        assert maximum > minimum, "maximum value must be greater than minimum value"
    if multiple_of is not None and maximum is not None:
        assert maximum > multiple_of, "maximum value must be greater than multiple_of"
    if multiple_of is None:
        if minimum is not None and maximum is None:
            if minimum == 0:
                return minimum, seed
            return minimum, minimum + seed
        if maximum is not None and minimum is None:
            return maximum - seed, maximum
    return minimum, maximum


def generate_constrained_number(
    minimum: Optional[T],
    maximum: Optional[T],
    multiple_of: Optional[T],
    method: Callable,
) -> T:
    """Generates a constrained number, output depends on the passed in callbacks"""
    if minimum is not None and maximum is not None:
        if multiple_of is None:
            return cast(T, method(minimum, maximum))
        if multiple_of >= minimum:
            return multiple_of
        result = minimum
        while not passes_pydantic_multiple_validator(result, multiple_of):
            result = round(method(minimum, maximum) / multiple_of) * multiple_of
        return result
    if multiple_of is not None:
        return multiple_of
    return cast(T, method())
