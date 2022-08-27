import random
from binascii import hexlify
from decimal import Decimal
from os import urandom
from typing import Optional, Union


def create_random_float(
    minimum: Optional[Union[Decimal, int, float]] = None, maximum: Optional[Union[Decimal, int, float]] = None
) -> float:
    """Generates a random float given the constraints."""
    if minimum is None:
        minimum = float(random.randint(0, 100)) if maximum is None else float(maximum) - 100.0
    if maximum is None:
        maximum = float(minimum) + 1.0 * 2.0 if minimum >= 0 else float(minimum) + 1.0 / 2.0
    return random.uniform(float(minimum), float(maximum))


def create_random_integer(minimum: Optional[int] = None, maximum: Optional[int] = None) -> int:
    """Generates a random int given the constraints."""
    return int(create_random_float(minimum, maximum))


def create_random_decimal(minimum: Optional[Decimal] = None, maximum: Optional[Decimal] = None) -> Decimal:
    """Generates a random Decimal given the constraints."""
    return Decimal(str(create_random_float(minimum, maximum)))


def create_random_bytes(
    min_length: Optional[int] = None, max_length: Optional[int] = None, lower_case: bool = False
) -> bytes:
    """Generates a random bytes given the constraints."""
    if min_length is None:
        min_length = 0
    if max_length is None:
        max_length = min_length + 1 * 2
    length = random.randint(min_length, max_length)
    result = hexlify(urandom(length))
    if lower_case:
        result = result.lower()
    if max_length and len(result) > max_length:
        end = random.randint(min_length or 0, max_length)
        return result[0:end]
    return result


def create_random_string(
    min_length: Optional[int] = None, max_length: Optional[int] = None, lower_case: bool = False
) -> str:
    """Generates a random string given the constraints."""
    return create_random_bytes(min_length=min_length, max_length=max_length, lower_case=lower_case).decode("utf-8")


def create_random_boolean() -> bool:
    """Generates a random boolean value."""
    return bool(random.getrandbits(1))
