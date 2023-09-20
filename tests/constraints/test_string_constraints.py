import re
from random import Random

import pytest
from hypothesis import given, settings
from hypothesis.strategies import booleans, integers

from polyfactory.exceptions import ParameterException
from polyfactory.value_generators.constrained_strings import handle_constrained_string_or_bytes

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
    to_lower: bool,
    min_length: int,
    max_length: int,
) -> None:
    if min_length < 0 or max_length < 0 or min_length > max_length:
        with pytest.raises(ParameterException):
            handle_constrained_string_or_bytes(
                random=Random(),
                t_type=str,
                lower_case=to_lower,
                upper_case=to_lower,
                min_length=min_length,
                max_length=max_length,
                pattern=None,
            )
    else:
        for regex in REGEXES:
            result = handle_constrained_string_or_bytes(
                random=Random(),
                t_type=str,
                lower_case=to_lower,
                upper_case=to_lower,
                min_length=min_length,
                max_length=max_length,
                pattern=None,
            )
            if to_lower:
                assert result == result.lower()
            if match := re.search(regex, result):
                assert match[0]
            assert len(result) >= min_length
            assert len(result) <= max_length


@given(booleans(), integers(max_value=10000), integers(max_value=10000))
def test_handle_constrained_string_with_min_length_and_max_length(
    to_lower: bool,
    min_length: int,
    max_length: int,
) -> None:
    if min_length < 0 or max_length < 0 or min_length > max_length:
        with pytest.raises(ParameterException):
            handle_constrained_string_or_bytes(
                random=Random(),
                t_type=str,
                lower_case=to_lower,
                upper_case=to_lower,
                min_length=min_length,
                max_length=max_length,
                pattern=None,
            )
    else:
        result = handle_constrained_string_or_bytes(
            random=Random(),
            t_type=str,
            lower_case=to_lower,
            upper_case=to_lower,
            min_length=min_length,
            max_length=max_length,
            pattern=None,
        )
        if to_lower:
            assert result == result.lower()
        assert len(result) >= min_length
        assert len(result) <= max_length


@given(booleans(), integers(max_value=10000))
def test_handle_constrained_string_with_min_length(to_lower: bool, min_length: int) -> None:
    if min_length < 0:
        with pytest.raises(ParameterException):
            handle_constrained_string_or_bytes(
                random=Random(),
                t_type=str,
                lower_case=to_lower,
                upper_case=to_lower,
                min_length=min_length,
                pattern=None,
            )
    else:
        result = handle_constrained_string_or_bytes(
            random=Random(),
            t_type=str,
            lower_case=to_lower,
            upper_case=to_lower,
            min_length=min_length,
            pattern=None,
        )
        if to_lower:
            assert result == result.lower()
        assert len(result) >= min_length


@given(booleans(), integers(max_value=10000))
def test_handle_constrained_string_with_max_length(to_lower: bool, max_length: int) -> None:
    if max_length < 0:
        with pytest.raises(ParameterException):
            handle_constrained_string_or_bytes(
                random=Random(),
                t_type=str,
                lower_case=to_lower,
                upper_case=to_lower,
                max_length=max_length,
                pattern=None,
            )
    else:
        result = handle_constrained_string_or_bytes(
            random=Random(),
            t_type=str,
            lower_case=to_lower,
            upper_case=to_lower,
            max_length=max_length,
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
