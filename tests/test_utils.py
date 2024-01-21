import random
import sys
from decimal import Decimal
from typing import Any, NewType, Union

import pytest
from hypothesis import given
from hypothesis.strategies import decimals, floats, integers

from pydantic import BaseModel

from polyfactory.factories.pydantic_factory import ModelFactory
from polyfactory.utils.helpers import unwrap_new_type
from polyfactory.utils.predicates import is_new_type, is_union
from polyfactory.value_generators.constrained_numbers import (
    is_multiply_of_multiple_of_in_range,
)


def test_is_union() -> None:
    class UnionTest(BaseModel):
        union: Union[int, str]
        no_union: Any

    class UnionTestFactory(ModelFactory):
        __model__ = UnionTest

    for field_meta in UnionTestFactory.get_model_fields():
        if field_meta.name == "union":
            assert is_union(field_meta.annotation)
        else:
            assert not is_union(field_meta.annotation)

    # for python 3.10 we need to run the test as well with the union_pipe operator
    if sys.version_info >= (3, 10):

        class UnionTestWithPipe(BaseModel):
            union_pipe: int | str | None  # Pipe syntax supported from Python 3.10 onwards
            union_normal: Union[int, str]
            no_union: Any

        class UnionTestWithPipeFactory(ModelFactory):
            __model__ = UnionTestWithPipe

        for field_meta in UnionTestWithPipeFactory.get_model_fields():
            if field_meta.name in ("union_pipe", "union_normal"):
                assert is_union(field_meta.annotation)
            else:
                assert not is_union(field_meta.annotation)


def test_is_new_type() -> None:
    assert is_new_type(NewType("MyInt", int))
    assert not is_new_type(int)


def test_unwrap_new_type_is_needed() -> None:
    MyInt = NewType("MyInt", int)
    WrappedInt = NewType("WrappedInt", MyInt)

    assert unwrap_new_type(MyInt) is int
    assert unwrap_new_type(WrappedInt) is int
    assert unwrap_new_type(int) is int


def test_is_multiply_of_multiple_of_in_range_extreme_cases() -> None:
    assert is_multiply_of_multiple_of_in_range(minimum=0.0, maximum=10.0, multiple_of=20.0)
    assert not is_multiply_of_multiple_of_in_range(minimum=5.0, maximum=10.0, multiple_of=20.0)

    assert is_multiply_of_multiple_of_in_range(minimum=1.0, maximum=1.0, multiple_of=0.33333333333)
    assert is_multiply_of_multiple_of_in_range(
        minimum=Decimal(1),
        maximum=Decimal(1),
        multiple_of=Decimal("0.33333333333"),
    )
    assert not is_multiply_of_multiple_of_in_range(minimum=Decimal(1), maximum=Decimal(1), multiple_of=Decimal("0.333"))

    assert is_multiply_of_multiple_of_in_range(minimum=5, maximum=5, multiple_of=5)

    # while multiple_of=0.0 leads to ZeroDivision exception in pydantic
    # it can handle values close to zero properly, so we should support this too
    assert is_multiply_of_multiple_of_in_range(minimum=10.0, maximum=20.0, multiple_of=1e-10)
    # test corner case found by peterschutt
    assert not is_multiply_of_multiple_of_in_range(
        minimum=Decimal("999999999.9999999343812775"),
        maximum=Decimal("999999999.990476"),
        multiple_of=Decimal("-0.556"),
    )


@given(
    floats(allow_nan=False, allow_infinity=False, min_value=1e-6, max_value=1000000000),
    integers(min_value=-100000, max_value=100000),
)
def test_is_multiply_of_multiple_of_in_range_for_floats(base_multiple_of: float, multiplier: int) -> None:
    if multiplier != 0:
        for multiple_of in [base_multiple_of, -base_multiple_of]:
            minimum, maximum = sorted(
                [
                    multiplier * multiple_of + random.random() * 100,
                    (multiplier + random.randint(1, 100)) * multiple_of + random.random() * 100,
                ],
            )
            assert is_multiply_of_multiple_of_in_range(minimum=minimum, maximum=maximum, multiple_of=multiple_of)

            minimum, maximum = sorted(
                [
                    (multiplier + (random.random() / 2 + 0.01)) * multiple_of,
                    (multiplier + (random.random() / 2 + 0.45)) * multiple_of,
                ],
            )
            assert not is_multiply_of_multiple_of_in_range(minimum=minimum, maximum=maximum, multiple_of=multiple_of)


@given(
    integers(min_value=-1000000000, max_value=1000000000),
    integers(min_value=-100000, max_value=100000),
)
def test_is_multiply_of_multiple_of_in_range_for_int(base_multiple_of: int, multiplier: int) -> None:
    if multiplier != 0 and base_multiple_of not in [-1, 0, 1]:
        for multiple_of in [base_multiple_of, -base_multiple_of]:
            minimum, maximum = sorted(
                [
                    multiplier * multiple_of + random.randint(1, 100),
                    (multiplier + random.randint(1, 100)) * multiple_of + random.randint(1, 100),
                ],
            )
            assert is_multiply_of_multiple_of_in_range(minimum=minimum, maximum=maximum, multiple_of=multiple_of)


@pytest.mark.skip(reason="fails on edge cases")
@given(
    decimals(min_value=Decimal("-1000000000"), max_value=Decimal("1000000000")),
    integers(min_value=-100000, max_value=100000),
)
def test_is_multiply_of_multiple_of_in_range_for_decimals(base_multiple_of: Decimal, multiplier: int) -> None:
    if multiplier != 0 and base_multiple_of != 0:
        for multiple_of in [base_multiple_of, -base_multiple_of]:
            minimum, maximum = sorted(
                [
                    multiplier * multiple_of + Decimal(random.random() * 100),
                    (multiplier + random.randint(1, 100)) * multiple_of + Decimal(random.random() * 100),
                ],
            )
            assert is_multiply_of_multiple_of_in_range(minimum=minimum, maximum=maximum, multiple_of=multiple_of)

            minimum, maximum = sorted(
                [
                    (multiplier + Decimal(random.random() / 2 + 0.01)) * multiple_of,
                    (multiplier + Decimal(random.random() / 2 + 0.45)) * multiple_of,
                ],
            )
            assert not is_multiply_of_multiple_of_in_range(minimum=minimum, maximum=maximum, multiple_of=multiple_of)
