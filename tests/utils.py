from decimal import Decimal
from typing import TypeVar

from pydantic.utils import almost_equal_floats

T = TypeVar("T", int, float, Decimal)


def passes_pydantic_multiple_validator(value: T, multiple_of: T) -> bool:
    if multiple_of == 0:
        return True
    mod = float(value) / float(multiple_of) % 1
    return almost_equal_floats(mod, 0.0) or almost_equal_floats(mod, 1.0)
