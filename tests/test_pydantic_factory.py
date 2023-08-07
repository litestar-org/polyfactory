from __future__ import annotations

import sys
from typing import Optional

import pytest
from pydantic import VERSION, BaseModel, Field, Json, ValidationError

from polyfactory.factories.pydantic_factory import ModelFactory


@pytest.mark.skipif(VERSION.startswith("2"), reason="pydantic v1 only functionality")
def test_const() -> None:
    class A(BaseModel):
        v: int = Field(1, const=True)

    class AFactory(ModelFactory[A]):
        __model__ = A

    for _ in range(5):
        assert AFactory.build()


def test_optional_with_constraints() -> None:
    """this is a flaky test - because it depends on randomness, hence it's been re-ran multiple times."""

    class A(BaseModel):
        a: Optional[int] = Field(None, ge=0, le=1)

    class AFactory(ModelFactory[A]):
        __model__ = A

    has_failed = False
    exception: Optional[Exception] = None
    for _ in range(100):
        try:
            assert isinstance(AFactory.build().a, (int, type(None)))
        except ValidationError as e:
            exception = e
            has_failed = True

    if has_failed:
        pytest.fail(reason=str(exception))


@pytest.mark.skipif(sys.version_info < (3, 10), reason="requires python3.9 or higher")
def test_list_unions() -> None:
    # issue: https://github.com/litestar-org/polyfactory/issues/300, no error reproduced
    class A(BaseModel):
        a: str

    class B(BaseModel):
        b: str

    class C(BaseModel):
        c: list[A] | list[B]

    class CFactory(ModelFactory[C]):
        __forward_ref_resolution_type_mapping__ = {"A": A, "B": B, "C": C}
        __model__ = C

    assert isinstance(CFactory.build().c, list)
    assert len(CFactory.build().c) > 0
    assert isinstance(CFactory.build().c[0], (A, B))


@pytest.mark.skipif(VERSION.startswith("1"), reason="only for Pydantic v2")
def test_json_type() -> None:
    class A(BaseModel):
        a: Json[int]

    class AFactory(ModelFactory[A]):
        __model__ = A

    assert isinstance(AFactory.build(), A)


@pytest.mark.skipif(VERSION.startswith("1"), reason="only for Pydantic v2")
def test_nested_json_type() -> None:
    class A(BaseModel):
        a: int

    class B(BaseModel):
        b: Json[A]

    class BFactory(ModelFactory[B]):
        __model__ = B

    assert isinstance(BFactory.build(), B)
