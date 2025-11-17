"""Tests to check that usage of pydantic v1 and v2 at the same time works."""

import sys
from typing import Annotated, Optional, Union

import pytest

import pydantic

from polyfactory.factories.pydantic_factory import ModelFactory

if pydantic.VERSION.startswith("1"):
    pytest.skip("only for pydantic v2", allow_module_level=True)

from pydantic import BaseModel as BaseModelV2

try:
    from pydantic.v1 import BaseModel as BaseModelV1
except ImportError:
    from pydantic import BaseModel as BaseModelV1  # type: ignore[assignment]

skip_pydantic_v1_on_py314 = pytest.mark.skipif(
    sys.version_info >= (3, 14),
    reason="pydantic v1 not supported on Python 3.14",
)


@pytest.mark.parametrize(
    "base_model",
    [
        pytest.param(BaseModelV1, marks=skip_pydantic_v1_on_py314),
        BaseModelV2,
    ],
)
def test_is_supported_type(base_model: type[Union[BaseModelV1, BaseModelV2]]) -> None:
    class Foo(base_model):  # type: ignore[valid-type, misc]
        ...

    assert ModelFactory.is_supported_type(Foo) is True


@pytest.mark.parametrize(
    "base_model",
    [
        pytest.param(BaseModelV1, marks=skip_pydantic_v1_on_py314),
        BaseModelV2,
    ],
)
def test_build(base_model: type[Union[BaseModelV1, BaseModelV2]]) -> None:
    class Foo(base_model):  # type: ignore[valid-type, misc]
        a: int
        b: str
        c: bool

    FooFactory = ModelFactory.create_factory(Foo)
    foo = FooFactory.build()

    assert isinstance(foo.a, int)
    assert isinstance(foo.b, str)
    assert isinstance(foo.c, bool)


@skip_pydantic_v1_on_py314
def test_build_v1_with_constrained_fields() -> None:
    from pydantic.v1.fields import Field

    ConstrainedInt = Annotated[int, Field(ge=100, le=200)]
    ConstrainedStr = Annotated[str, Field(min_length=1, max_length=3)]

    class Foo(BaseModelV1):
        a: ConstrainedInt
        b: ConstrainedStr
        c: Union[ConstrainedInt, ConstrainedStr]
        d: Optional[ConstrainedInt]
        e: Optional[Union[ConstrainedInt, ConstrainedStr]]
        f: list[ConstrainedInt]
        g: dict[ConstrainedInt, ConstrainedStr]

    ModelFactory.create_factory(Foo).build()


def test_build_v2_with_constrained_fields() -> None:
    from pydantic.fields import Field

    ConstrainedInt = Annotated[int, Field(ge=100, le=200)]
    ConstrainedStr = Annotated[str, Field(min_length=1, max_length=3)]

    class Foo(pydantic.BaseModel):  # pyright: ignore[reportGeneralTypeIssues]
        a: ConstrainedInt
        b: ConstrainedStr
        c: Union[ConstrainedInt, ConstrainedStr]
        d: Optional[ConstrainedInt]
        e: Optional[Union[ConstrainedInt, ConstrainedStr]]
        f: list[ConstrainedInt]
        g: dict[ConstrainedInt, ConstrainedStr]

    ModelFactory.create_factory(Foo).build()


def test_variadic_tuple_length() -> None:
    class Foo(pydantic.BaseModel):
        bar: tuple[int, ...]

    class Factory(ModelFactory[Foo]):
        __randomize_collection_length__ = True
        __min_collection_length__ = 7
        __max_collection_length__ = 8

    result = Factory.build()
    assert 7 <= len(result.bar) <= 8


@skip_pydantic_v1_on_py314
def test_build_v1_with_url_and_email_types() -> None:
    from pydantic.v1 import AnyHttpUrl, AnyUrl, EmailStr, HttpUrl, NameEmail

    class Foo(BaseModelV1):
        http_url: HttpUrl
        any_http_url: AnyHttpUrl
        any_url: AnyUrl
        email_str: EmailStr
        name_email: NameEmail
        composed: tuple[HttpUrl, AnyHttpUrl, AnyUrl, EmailStr, NameEmail]

    ModelFactory.create_factory(Foo).build()
