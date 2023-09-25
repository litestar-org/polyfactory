from random import Random

import pytest
from hypothesis import given
from hypothesis.strategies import booleans, integers

from polyfactory.exceptions import ParameterException
from polyfactory.value_generators.constrained_strings import handle_constrained_string_or_bytes


@given(booleans(), integers(max_value=10000), integers(max_value=10000))
def test_handle_constrained_bytes_with_min_length_and_max_length(
    to_lower: bool,
    min_length: int,
    max_length: int,
) -> None:
    if min_length < 0 or max_length < 0 or min_length > max_length:
        with pytest.raises(ParameterException):
            handle_constrained_string_or_bytes(
                random=Random(),
                t_type=bytes,
                min_length=min_length,
                max_length=max_length,
                pattern=None,
            )
    else:
        result = handle_constrained_string_or_bytes(
            random=Random(),
            t_type=bytes,
            min_length=min_length,
            max_length=max_length,
            pattern=None,
        )
        if to_lower:
            assert result == result.lower()
        assert len(result) >= min_length
        assert len(result) <= max_length


@given(booleans(), integers(max_value=10000))
def test_handle_constrained_bytes_with_min_length(to_lower: bool, min_length: int) -> None:
    if min_length < 0:
        with pytest.raises(ParameterException):
            handle_constrained_string_or_bytes(
                random=Random(),
                t_type=bytes,
                min_length=min_length,
                pattern=None,
            )
    else:
        result = handle_constrained_string_or_bytes(
            random=Random(),
            t_type=bytes,
            min_length=min_length,
            pattern=None,
        )
        if to_lower:
            assert result == result.lower()
        assert len(result) >= min_length


@given(booleans(), integers(max_value=10000))
def test_handle_constrained_bytes_with_max_length(to_lower: bool, max_length: int) -> None:
    if max_length < 0:
        with pytest.raises(ParameterException):
            handle_constrained_string_or_bytes(
                random=Random(),
                t_type=bytes,
                max_length=max_length,
                pattern=None,
            )
    else:
        result = handle_constrained_string_or_bytes(
            random=Random(),
            t_type=bytes,
            max_length=max_length,
            pattern=None,
        )
        if to_lower:
            assert result == result.lower()
        assert len(result) <= max_length
