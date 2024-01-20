from typing import List, Optional, Tuple, Union

import pytest
from annotated_types import Ge, MinLen
from pydantic import BaseModel
from typing_extensions import Annotated

from polyfactory.factories.pydantic_factory import ModelFactory


def test_union_types() -> None:
    class A(BaseModel):
        a: Union[List[str], List[int]]
        b: Union[str, List[int]]
        c: List[Union[Tuple[int, int], Tuple[str, int]]]

    AFactory = ModelFactory.create_factory(A)

    assert AFactory.build()


def test_collection_unions_with_models() -> None:
    class A(BaseModel):
        a: int

    class B(BaseModel):
        a: str

    class C(BaseModel):
        a: Union[List[A], List[B]]
        b: List[Union[A, B]]

    CFactory = ModelFactory.create_factory(C)

    assert CFactory.build()


def test_constrained_union_types() -> None:
    class A(BaseModel):
        a: Union[Annotated[List[str], MinLen(100)], Annotated[int, Ge(1000)]]
        b: Union[List[Annotated[str, MinLen(100)]], int]

    AFactory = ModelFactory.create_factory(A)

    assert AFactory.build()


@pytest.mark.parametrize("allow_none", (True, False))
def test_optional_type(allow_none: bool) -> None:
    class A(BaseModel):
        a: Union[str, None]
        b: Optional[str]
        c: Optional[Union[str, int, List[int]]]

    class AFactory(ModelFactory[A]):
        __model__ = A

        __allow_none_optionals__ = allow_none

    assert AFactory.build()
