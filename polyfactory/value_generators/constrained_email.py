from __future__ import annotations

from string import ascii_lowercase
from typing import TYPE_CHECKING

from polyfactory.exceptions import ParameterException
from polyfactory.value_generators.constrained_strings import _validate_length

if TYPE_CHECKING:
    from random import Random

_MIN_EMAIL_LENGTH = 5
_MAX_EMAIL_LENGTH = 254
_MAX_LOCAL_LENGTH = 64
_MAX_LABEL_LENGTH = 63


def handle_constrained_email(random: Random, min_length: int | None = None, max_length: int | None = None) -> str:
    """Generate an ASCII email address within the requested length bounds.

    :param random: An instance of random.
    :param min_length: A minimum length for the complete address.
    :param max_length: A maximum length for the complete address.
    :raises ParameterException: If no valid email address fits the bounds.
    :returns: An email address with at most 64 local-part characters and 63 characters per domain label.
    """
    _validate_length(min_length=min_length, max_length=max_length)
    minimum = max(_MIN_EMAIL_LENGTH, min_length or 0)
    maximum = min(_MAX_EMAIL_LENGTH, max_length if max_length is not None else _MAX_EMAIL_LENGTH)
    if minimum > maximum:
        msg = "email length constraints must allow an address between 5 and 254 characters"
        raise ParameterException(msg)

    length = random.randint(minimum, maximum)
    # Leave room for a dotted domain even at the shortest supported lengths.
    local_length = min(_MAX_LOCAL_LENGTH, length - min(len("a.com"), length - 2) - 1)
    domain_length = length - local_length - 1
    suffix = ".com" if domain_length >= len("a.com") else ".io" if domain_length == len("a.io") else ".a"
    remaining = domain_length - len(suffix)
    labels = []
    while remaining > _MAX_LABEL_LENGTH:
        # A separator must always be followed by a nonempty label.
        label_length = min(_MAX_LABEL_LENGTH, remaining - 2)
        labels.append("".join(random.choices(ascii_lowercase, k=label_length)))
        remaining -= label_length + 1
    labels.append("".join(random.choices(ascii_lowercase, k=remaining)))
    local = "".join(random.choices(ascii_lowercase, k=local_length))
    return f"{local}@{'.'.join(labels)}{suffix}"
