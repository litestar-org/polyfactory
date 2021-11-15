import re
from decimal import Decimal
from random import random, uniform, randint
from typing import Optional, Tuple, TypeVar, Union

from exrex import getone
from faker import Faker
from pydantic import (
    ConstrainedDecimal,
    ConstrainedFloat,
    ConstrainedInt,
    ConstrainedStr,
    confloat,
)
from typing_extensions import Type

from pydantic_factories.exceptions import ParameterError

T = TypeVar("T", Decimal, int, float)


def _get_constrained_numerical_values(
    lt: Optional[T],
    le: Optional[T],
    gt: Optional[T],
    ge: Optional[T],
    increment: T,
    t_type: Type[T],
    multiple_of: Optional[T] = None,
) -> Tuple[Optional[T], Optional[T]]:
    seed = t_type(random() * 10)
    minimum = ge if ge is not None else gt + increment if gt is not None else None
    maximum = le if le is not None else lt - increment if lt is not None else None
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


def handle_constrained_decimal(field: ConstrainedDecimal, faker: Faker) -> Decimal:
    multiple_of = field.multiple_of
    if multiple_of == 0:
        return Decimal(0)
    elif multiple_of:
        raise ParameterError(
            "generating Decimals with multiple_of is not supported, please specify a value in the factory"
        )
    minimum, maximum = _get_constrained_numerical_values(
        gt=field.gt, ge=field.ge, lt=field.lt, le=field.le, increment=Decimal(0.1), t_type=Decimal
    )

    return Decimal(
        handle_constrained_float(
            confloat(
                ge=float(minimum) if minimum else None,
                le=float(maximum) if maximum else None,
            ),
            faker,
        )
    )


def handle_constrained_float(field: ConstrainedFloat, faker: Faker) -> float:
    multiple_of = field.multiple_of
    if multiple_of == 0:
        return 0
    minimum, maximum = _get_constrained_numerical_values(
        gt=field.gt, ge=field.ge, lt=field.lt, le=field.le, increment=0.0001, t_type=float, multiple_of=multiple_of
    )
    if minimum is not None and maximum is not None:
        if multiple_of is None:
            return uniform(minimum, maximum)
        if multiple_of >= minimum:
            return multiple_of
        return round(uniform(minimum, maximum) / multiple_of) * multiple_of
    if multiple_of is not None:
        return multiple_of
    return faker.pyfloat()


def handle_constrained_int(field: ConstrainedInt, faker: Faker) -> int:
    multiple_of = field.multiple_of
    if multiple_of == 0:
        return 0
    minimum, maximum = _get_constrained_numerical_values(
        gt=field.gt, ge=field.ge, lt=field.lt, le=field.le, increment=1, t_type=int, multiple_of=multiple_of
    )
    if minimum is not None and maximum is not None:
        if multiple_of is None:
            return randint(minimum, maximum)
        if multiple_of >= minimum:
            return multiple_of
        return round(randint(minimum, maximum) / multiple_of) * multiple_of
    if multiple_of is not None:
        return multiple_of
    return faker.pyint()


def handle_constrained_string(field: ConstrainedStr, faker: Faker) -> str:
    to_lower = field.to_lower
    min_length = field.min_length
    max_length = field.max_length
    regex = re.compile(field.regex) if field.regex else None
    method = lambda: getone(regex) if regex else faker.pystr
    result = method()
    if min_length and len(result) < min_length:
        while len(result) < min_length:
            result += method()
    if to_lower:
        result = result.lower()
    if max_length and len(result) > max_length:
        return result[:max_length]
    return result
