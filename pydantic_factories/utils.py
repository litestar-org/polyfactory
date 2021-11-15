import re
from decimal import Decimal
from random import uniform, random
from typing import Union

from exrex import getone
from faker import Faker
from pydantic import ConstrainedFloat, ConstrainedInt, ConstrainedStr, ConstrainedDecimal
from typing_extensions import Type


def handle_constrained_decimal(field: ConstrainedDecimal) -> Decimal:
    pass


def handle_constrained_float(field: ConstrainedFloat, faker: Faker) -> float:
    base, minimum, maximum, seed = field.multiple_of, field.ge, field.le, random() * 10
    if base == 0:
        return 0
    if maximum is None and field.lt is not None:
        maximum = field.lt - 0.1
    if minimum is None and field.gt is not None:
        minimum = field.gt + 0.1
    if base is None:
        if minimum is not None and maximum is not None:
            assert minimum < maximum, "minimum must be lower then maximum"
            return uniform(minimum, maximum)
        if minimum is not None:
            result = uniform(minimum, minimum * seed)
            return result if minimum >= 0 else result * -1
        if maximum is not None:
            if maximum > 0:
                return uniform(maximum / seed, maximum)
            # this will fail with very small numbers
            return uniform(maximum * seed, maximum)
        return faker.pyfloat()
    if minimum is None and maximum is None:
        return float(base)
    if minimum is not None:
        if maximum is None:
            return base
    if maximum is not None:
        assert maximum > base, "maximum value must be greater then multiple_of"
        if minimum is None:
            return base
    assert minimum < maximum, "minimum must be lower then maximum"
    if base >= minimum:
        return base
    return round(uniform(minimum, maximum) / base) * base


def handle_constrained_int(field: ConstrainedInt) -> int:
    pass


def handle_constrained_number(
    field: Union[ConstrainedInt, ConstrainedFloat],
    inner_field_type: Union[Type[int], Type[float], Type[Decimal]],
    faker: Faker,
) -> Union[int, float, Decimal]:
    increment = 1 if inner_field_type == int else 0.1
    if inner_field_type == int:
        method = faker.pyint
    elif inner_field_type == float:
        method = faker.pyfloat
    else:
        method = faker.pydecimal
    kwargs = {}
    if field.gt is not None:
        kwargs["min_value"] = field.gt + increment
    elif field.ge is not None:
        kwargs["min_value"] = field.ge
    if field.lt is not None:
        kwargs["max_value"] = field.lt - increment
    elif field.le is not None:
        kwargs["max_value"] = field.le
    if hasattr(field, "max_digits") and getattr(field, "max_digits") is not None:
        kwargs["left_digits"] = field.max_digits
    if hasattr(field, "decimal_places") and getattr(field, "decimal_places") is not None:
        kwargs["right_digits"] = field.decimal_places
    result = method(**kwargs)
    if field.multiple_of is not None:
        kwargs.setdefault("min_value", field.multiple_of)
        kwargs.setdefault("max_value", field.multiple_of)
        value = field.multiple_of * round(result / field.multiple_of)
        if kwargs.get("right_digits"):
            return Decimal(round(value, kwargs.get("right_digits")))
        return inner_field_type(field.multiple_of * round(result / field.multiple_of))
    return result


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
