from decimal import Decimal
from random import random
from typing import Callable, Optional, Tuple, TypeVar

from pydantic import ConstrainedDecimal, ConstrainedFloat, ConstrainedInt
from typing_extensions import Type

from pydantic_factories.utils import (
    create_random_decimal,
    create_random_float,
    create_random_integer,
)

T = TypeVar("T", Decimal, int, float)


def get_increment(t_type: Type[T]) -> T:
    """gets a small increment base to add to constrained values, i.e. lt/gt entries"""
    if t_type == int:
        return t_type(1)
    if t_type == float:
        return t_type(0.0001)
    return t_type(0.001)


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
    seed = t_type(random() * 10)
    minimum = get_value_or_none(ge, gt, get_increment(t_type))
    maximum = get_value_or_none(le, lt, -get_increment(t_type))
    if minimum is not None and maximum is not None:
        assert minimum < maximum, "minimum must be lower then maximum"
    if multiple_of is not None and maximum is not None:
        assert maximum > multiple_of, "maximum value must be greater then multiple_of"
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
            return method(minimum, maximum)
        if multiple_of >= minimum:
            return multiple_of
        return round(method(minimum, maximum) / multiple_of) * multiple_of
    if multiple_of is not None:
        return multiple_of
    return method()


def handle_constrained_decimal(field: ConstrainedDecimal) -> Decimal:
    """
    Handles 'ConstrainedDecimal' instances

    TODO: extend support for decimal places
    """
    multiple_of = field.multiple_of
    if multiple_of == 0:
        return Decimal(0)
    assert multiple_of is None, "generating Decimals with multiple_of is not supported"
    minimum, maximum = get_constrained_number_range(gt=field.gt, ge=field.ge, lt=field.lt, le=field.le, t_type=Decimal)  # type: ignore
    return generate_constrained_number(  # type: ignore
        minimum=minimum,
        maximum=maximum,
        multiple_of=None,
        method=create_random_decimal,
    )


def handle_constrained_float(field: ConstrainedFloat) -> float:
    """
    Handles 'ConstrainedFloat' instances
    """
    multiple_of = field.multiple_of
    if multiple_of == 0:
        return 0
    minimum, maximum = get_constrained_number_range(
        gt=field.gt, ge=field.ge, lt=field.lt, le=field.le, t_type=float, multiple_of=multiple_of
    )
    return generate_constrained_number(
        minimum=minimum,
        maximum=maximum,
        multiple_of=multiple_of,
        method=create_random_float,
    )


def handle_constrained_int(field: ConstrainedInt) -> int:
    """
    Handles 'ConstrainedInt' instances
    """
    multiple_of = field.multiple_of
    if multiple_of == 0:
        return 0
    minimum, maximum = get_constrained_number_range(
        gt=field.gt, ge=field.ge, lt=field.lt, le=field.le, t_type=int, multiple_of=multiple_of
    )
    return generate_constrained_number(
        minimum=minimum, maximum=maximum, multiple_of=multiple_of, method=create_random_integer
    )
