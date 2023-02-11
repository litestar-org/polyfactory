from typing import TYPE_CHECKING, Callable, Optional, Pattern, TypeVar, Union, cast

from polyfactory.exceptions import ParameterError
from polyfactory.value_generators.primitives import (
    create_random_bytes,
    create_random_string,
)
from polyfactory.value_generators.regex import RegexFactory

T = TypeVar("T", bound=Union[bytes, str])

if TYPE_CHECKING:
    from random import Random


def _validate_length(
    min_length: Optional[int] = None,
    max_length: Optional[int] = None,
) -> None:
    """

    :param min_length:
    :param max_length:
    :return:
    """
    if min_length is not None and min_length < 0:
        raise ParameterError("min_length must be greater or equal to 0")

    if max_length is not None and max_length < 0:
        raise ParameterError("max_length must be greater or equal to 0")

    if max_length is not None and min_length is not None and max_length < min_length:
        raise ParameterError("max_length must be greater than min_length")


def _generate_pattern(
    random: "Random",
    t_type: Callable[[], T],
    pattern: Union[str, Pattern],
    lower_case: bool = False,
    upper_case: bool = False,
    min_length: Optional[int] = None,
    max_length: Optional[int] = None,
) -> T:
    """

    :param random:
    :param t_type:
    :param pattern:
    :param lower_case:
    :param upper_case:
    :param min_length:
    :param max_length:
    :return:
    """
    regex_factory = RegexFactory(random=random)
    result = regex_factory(pattern)
    if min_length:
        while len(result) < min_length:
            result += regex_factory(pattern)

    if max_length is not None and len(result) > max_length:
        result = result[:max_length]

    if lower_case:
        result = result.lower()

    if upper_case:
        result = result.upper()

    if t_type is str:
        return cast("T", result)
    return cast("T", result.encode())


def handle_constrained_string_or_bytes(
    random: "Random",
    t_type: Callable[[], T],
    lower_case: bool = False,
    upper_case: bool = False,
    min_length: Optional[int] = None,
    max_length: Optional[int] = None,
    pattern: Optional[Union[str, Pattern]] = None,
) -> T:
    """

    :param random:
    :param t_type:
    :param lower_case:
    :param upper_case:
    :param min_length:
    :param max_length:
    :param pattern:
    :return:
    """
    _validate_length(min_length=min_length, max_length=max_length)

    if max_length == 0:
        return t_type()

    if pattern:
        return _generate_pattern(
            random=random,
            t_type=t_type,
            pattern=pattern,
            lower_case=lower_case,
            upper_case=upper_case,
            min_length=min_length,
            max_length=max_length,
        )

    if t_type is str:
        return cast(
            "T",
            create_random_string(min_length=min_length, max_length=max_length, lower_case=lower_case, random=random),
        )

    return cast(
        "T", create_random_bytes(min_length=min_length, max_length=max_length, lower_case=lower_case, random=random)
    )
