import re
from random import Random
from typing import Optional

import pytest
from hypothesis import given, settings
from hypothesis.strategies import booleans, integers
from pydantic import ConstrainedStr

from polyfactory.exceptions import ParameterExceptionError
from polyfactory.value_generators.constrainted_strings import (
    handle_constrained_string_or_bytes,
)


def create_constrained_field(
    to_lower: bool, min_length: Optional[int] = None, max_length: Optional[int] = None
) -> ConstrainedStr:
    field = ConstrainedStr()
    field.max_length = max_length
    field.min_length = min_length
    field.to_lower = to_lower
    return field


REGEXES = [
    r"(a|b|c)xz",
    r"a|b",
    r"[0-9]{2,4}",
    r"a{2,3}",
    r"ma?n",
    r"ma+n",
    r"ma*n",
    r"a$",
    r"\Athe",
    r"\bfoo",
    r"foo\b",
    r"\Bfoo",
    r"foo\B",
]


@settings(deadline=600)
@given(
    booleans(),
    integers(min_value=5, max_value=100),
    integers(min_value=5, max_value=100),
)
def test_handle_constrained_string_with_min_length_and_max_length_and_regex(
    to_lower: bool, min_length: int, max_length: int
) -> None:
    field = create_constrained_field(to_lower=to_lower, min_length=min_length, max_length=max_length)
    if min_length < 0 or max_length < 0 or min_length > max_length:
        with pytest.raises(ParameterExceptionError):
            handle_constrained_string_or_bytes(
                random=Random(),
                t_type=str,
                lower_case=field.to_lower,
                upper_case=field.to_lower,
                min_length=field.min_length,
                max_length=field.max_length,
                pattern=None,
            )
    else:
        for regex in REGEXES:
            field.regex = regex
            result = handle_constrained_string_or_bytes(
                random=Random(),
                t_type=str,
                lower_case=field.to_lower,
                upper_case=field.to_lower,
                min_length=field.min_length,
                max_length=field.max_length,
                pattern=None,
            )
            if to_lower:
                assert result == result.lower()
            match = re.search(regex, result)

            if match:
                assert match.group(0)
            assert len(result) >= min_length
            assert len(result) <= max_length


@given(booleans(), integers(max_value=10000), integers(max_value=10000))
def test_handle_constrained_string_with_min_length_and_max_length(
    to_lower: bool, min_length: int, max_length: int
) -> None:
    field = create_constrained_field(to_lower=to_lower, min_length=min_length, max_length=max_length)
    if min_length < 0 or max_length < 0 or min_length > max_length:
        with pytest.raises(ParameterExceptionError):
            handle_constrained_string_or_bytes(
                random=Random(),
                t_type=str,
                lower_case=field.to_lower,
                upper_case=field.to_lower,
                min_length=field.min_length,
                max_length=field.max_length,
                pattern=None,
            )
    else:
        result = handle_constrained_string_or_bytes(
            random=Random(),
            t_type=str,
            lower_case=field.to_lower,
            upper_case=field.to_lower,
            min_length=field.min_length,
            max_length=field.max_length,
            pattern=None,
        )
        if to_lower:
            assert result == result.lower()
        assert len(result) >= min_length
        assert len(result) <= max_length


@given(booleans(), integers(max_value=10000))
def test_handle_constrained_string_with_min_length(to_lower: bool, min_length: int) -> None:
    field = create_constrained_field(to_lower=to_lower, min_length=min_length)
    if min_length < 0:
        with pytest.raises(ParameterExceptionError):
            handle_constrained_string_or_bytes(
                random=Random(),
                t_type=str,
                lower_case=field.to_lower,
                upper_case=field.to_lower,
                min_length=field.min_length,
                max_length=field.max_length,
                pattern=None,
            )
    else:
        result = handle_constrained_string_or_bytes(
            random=Random(),
            t_type=str,
            lower_case=field.to_lower,
            upper_case=field.to_lower,
            min_length=field.min_length,
            max_length=field.max_length,
            pattern=None,
        )
        if to_lower:
            assert result == result.lower()
        assert len(result) >= min_length


@given(booleans(), integers(max_value=10000))
def test_handle_constrained_string_with_max_length(to_lower: bool, max_length: int) -> None:
    field = create_constrained_field(to_lower=to_lower, max_length=max_length)
    if max_length < 0:
        with pytest.raises(ParameterExceptionError):
            handle_constrained_string_or_bytes(
                random=Random(),
                t_type=str,
                lower_case=field.to_lower,
                upper_case=field.to_lower,
                min_length=field.min_length,
                max_length=field.max_length,
                pattern=None,
            )
    else:
        result = handle_constrained_string_or_bytes(
            random=Random(),
            t_type=str,
            lower_case=field.to_lower,
            upper_case=field.to_lower,
            min_length=field.min_length,
            max_length=field.max_length,
            pattern=None,
        )
        if to_lower:
            assert result == result.lower()
        assert len(result) <= max_length


def test_pattern() -> None:
    result = handle_constrained_string_or_bytes(
        random=Random(),
        t_type=str,
        lower_case=False,
        upper_case=True,
        min_length=6,
        max_length=10,
        pattern="abc",
    )
    assert len(result) >= 6
    assert len(result) <= 10
    assert result.isupper()

    result = handle_constrained_string_or_bytes(
        random=Random(),
        t_type=str,
        lower_case=True,
        upper_case=False,
        min_length=6,
        max_length=10,
        pattern="abc",
    )
    assert len(result) >= 6
    assert len(result) <= 10
    assert not result.isupper()
