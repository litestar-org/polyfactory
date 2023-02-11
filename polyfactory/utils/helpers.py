from types import NoneType
from typing import Any, get_args

from polyfactory.utils.predicates import is_new_type, is_optional_union, is_union


def unwrap_new_type(value: Any) -> Any:
    """Returns base type if given value is a type derived with NewType, otherwise value.

    :param value:
    :return:
    """
    while is_new_type(value):
        value = value.__supertype__

    return value


def unwrap_union(value: Any) -> Any:
    """

    :param value:
    :return:
    """
    while is_union(value):
        value = get_args(value)[0]
    return value


def unwrap_optional(value: Any) -> Any:
    """

    :param value:
    :return:
    """
    while is_optional_union(value):
        args = get_args(value)
        value = args[0] if args[0] is not NoneType else args[1]
    return value


def unwrap_args(value: Any) -> Any:
    """

    :param value:
    :return:
    """
    while is_optional_union(value) or is_union(value) or is_new_type(value):
        if is_new_type(value):
            value = unwrap_new_type(value)
        elif is_optional_union(value):
            value = unwrap_optional(value)
        else:
            value = unwrap_union(value)
    return get_args(value)
