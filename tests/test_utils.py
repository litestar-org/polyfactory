import sys
from decimal import Decimal
from typing import Any, NewType, Union

from pydantic import BaseModel

from pydantic_factories.factory import ModelFactory
from pydantic_factories.utils import (
    is_multiply_of_multiple_of_in_range,
    is_new_type,
    is_union,
    unwrap_new_type_if_needed,
)


def test_is_union() -> None:
    class UnionTest(BaseModel):
        union: Union[int, str]
        no_union: Any

    class UnionTestFactory(ModelFactory):
        __model__ = UnionTest

    for field_name, model_field in UnionTestFactory.get_model_fields(UnionTestFactory._get_model()):
        if field_name == "union":
            assert is_union(model_field)
        else:
            assert not is_union(model_field)

    # for python 3.10 we need to run the test as well with the union_pipe operator
    if sys.version_info >= (3, 10):

        class UnionTestWithPipe(BaseModel):
            union_pipe: int | str | None  # Pipe syntax supported from Python 3.10 onwards
            union_normal: Union[int, str]
            no_union: Any

        class UnionTestWithPipeFactory(ModelFactory):
            __model__ = UnionTestWithPipe

        for field_name, model_field in UnionTestWithPipeFactory.get_model_fields(UnionTestWithPipeFactory._get_model()):
            if field_name in ("union_pipe", "union_normal"):
                assert is_union(model_field)
            else:
                assert not is_union(model_field)


def test_is_new_type() -> None:
    MyInt = NewType("MyInt", int)

    assert is_new_type(MyInt)
    assert not is_new_type(int)


def test_unwrap_new_type_is_needed() -> None:
    MyInt = NewType("MyInt", int)
    WrappedInt = NewType("WrappedInt", MyInt)

    assert unwrap_new_type_if_needed(MyInt) is int
    assert unwrap_new_type_if_needed(WrappedInt) is int
    assert unwrap_new_type_if_needed(int) is int


def test_is_multiply_of_multiple_of_in_range_extreme_cases() -> None:
    assert is_multiply_of_multiple_of_in_range(minimum=None, maximum=10.0, multiple_of=20.0)
    assert not is_multiply_of_multiple_of_in_range(minimum=5.0, maximum=10.0, multiple_of=20.0)

    assert is_multiply_of_multiple_of_in_range(minimum=1.0, maximum=1.0, multiple_of=0.33333333333)
    assert is_multiply_of_multiple_of_in_range(
        minimum=Decimal(1), maximum=Decimal(1), multiple_of=Decimal("0.33333333333")
    )
    assert not is_multiply_of_multiple_of_in_range(minimum=Decimal(1), maximum=Decimal(1), multiple_of=Decimal("0.333"))

    assert is_multiply_of_multiple_of_in_range(minimum=5, maximum=5, multiple_of=5)

    # while multiple_of=0.0 leads to ZeroDivision exception in pydantic
    # it can handle values close to zero properly so we should support this too
    assert is_multiply_of_multiple_of_in_range(minimum=10.0, maximum=20.0, multiple_of=1e-10)
