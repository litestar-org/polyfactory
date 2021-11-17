from random import randint

from exrex import getone  # pylint: disable=import-error
from faker import Faker
from pydantic import ConstrainedStr


def handle_constrained_string(field: ConstrainedStr, faker: Faker) -> str:
    """Handles ConstrainedStr and Fields with string constraints"""
    to_lower = field.to_lower
    min_length = field.min_length
    max_length = field.max_length

    assert min_length >= 0 if min_length is not None else True, "min_length must be greater or equal to 0"
    assert max_length >= 0 if max_length is not None else True, "max_length must be greater or equal to 0"
    if max_length is not None and min_length is not None:
        assert max_length >= min_length, "max_length must be greater than min_length"
    if max_length == 0:
        return ""
    if field.regex:
        result = getone(str(field.regex))
        if min_length:
            while len(result) < min_length:
                result += getone(str(field.regex))
    else:
        min_chars = min_length or 0
        max_chars = max_length if max_length is not None else min_chars + 1 * 2
        result = faker.pystr(min_chars=min_chars, max_chars=max_chars)
    if to_lower:
        result = result.lower()
    if max_length and len(result) > max_length:
        end = randint(min_length or 0, max_length)
        return result[0:end]
    return result
