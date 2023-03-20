from random import Random
from typing import Optional

import pytest
from hypothesis import given
from hypothesis.strategies import booleans, integers
from pydantic import ConstrainedBytes

from polyfactory.exceptions import ParameterExceptionError
from polyfactory.value_generators.constrained_strings import (
    handle_constrained_string_or_bytes,
)


def create_constrained_field(
    to_lower: bool, min_length: Optional[int] = None, max_length: Optional[int] = None
) -> ConstrainedBytes:
    field = ConstrainedBytes()
    field.max_length = max_length
    field.min_length = min_length
    field.to_lower = to_lower
    return field


@given(booleans(), integers(max_value=10000), integers(max_value=10000))
def test_handle_constrained_bytes_with_min_length_and_max_length(
    to_lower: bool, min_length: int, max_length: int
) -> None:
    field = create_constrained_field(to_lower=to_lower, min_length=min_length, max_length=max_length)
    if min_length < 0 or max_length < 0 or min_length > max_length:
        with pytest.raises(ParameterExceptionError):
            handle_constrained_string_or_bytes(
                random=Random(),
                t_type=bytes,
                lower_case=field.to_lower,
                upper_case=field.to_lower,
                min_length=field.min_length,
                max_length=field.max_length,
                pattern=None,
            )
    else:
        result = handle_constrained_string_or_bytes(
            random=Random(),
            t_type=bytes,
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
def test_handle_constrained_bytes_with_min_length(to_lower: bool, min_length: int) -> None:
    field = create_constrained_field(to_lower=to_lower, min_length=min_length)
    if min_length < 0:
        with pytest.raises(ParameterExceptionError):
            handle_constrained_string_or_bytes(
                random=Random(),
                t_type=bytes,
                lower_case=field.to_lower,
                upper_case=field.to_lower,
                min_length=field.min_length,
                max_length=field.max_length,
                pattern=None,
            )
    else:
        result = handle_constrained_string_or_bytes(
            random=Random(),
            t_type=bytes,
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
def test_handle_constrained_bytes_with_max_length(to_lower: bool, max_length: int) -> None:
    field = create_constrained_field(to_lower=to_lower, max_length=max_length)
    if max_length < 0:
        with pytest.raises(ParameterExceptionError):
            handle_constrained_string_or_bytes(
                random=Random(),
                t_type=bytes,
                lower_case=field.to_lower,
                upper_case=field.to_lower,
                min_length=field.min_length,
                max_length=field.max_length,
                pattern=None,
            )
    else:
        result = handle_constrained_string_or_bytes(
            random=Random(),
            t_type=bytes,
            lower_case=field.to_lower,
            upper_case=field.to_lower,
            min_length=field.min_length,
            max_length=field.max_length,
            pattern=None,
        )
        if to_lower:
            assert result == result.lower()
        assert len(result) <= max_length
