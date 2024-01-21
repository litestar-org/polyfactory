"""Tests to check that usage of pydantic v1 and v2 at the same time works."""

from typing import Dict, List, Optional, Type, Union

import pytest
from typing_extensions import Annotated

import pydantic

from polyfactory.factories.pydantic_factory import ModelFactory

if pydantic.VERSION.startswith("1"):
    pytest.skip("only for pydantic v2", allow_module_level=True)

from pydantic import BaseModel as BaseModelV2

try:
    from pydantic.v1 import BaseModel as BaseModelV1
except ImportError:
    from pydantic import BaseModel as BaseModelV1  # type: ignore[assignment]


@pytest.mark.parametrize("base_model", [BaseModelV1, BaseModelV2])
def test_is_supported_type(base_model: Type[Union[BaseModelV1, BaseModelV2]]) -> None:
    class Foo(base_model):  # type: ignore[valid-type, misc]
        ...

    assert ModelFactory.is_supported_type(Foo) is True


@pytest.mark.parametrize("base_model", [BaseModelV1, BaseModelV2])
def test_build(base_model: Type[Union[BaseModelV1, BaseModelV2]]) -> None:
    class Foo(base_model):  # type: ignore[valid-type, misc]
        a: int
        b: str
        c: bool

    FooFactory = ModelFactory.create_factory(Foo)
    foo = FooFactory.build()

    assert isinstance(foo.a, int)
    assert isinstance(foo.b, str)
    assert isinstance(foo.c, bool)


def test_build_v1_with_contrained_fields() -> None:
    from pydantic.v1.fields import Field

    ConstrainedInt = Annotated[int, Field(ge=100, le=200)]
    ConstrainedStr = Annotated[str, Field(min_length=1, max_length=3)]

    class Foo(pydantic.v1.BaseModel):  # pyright: ignore[reportGeneralTypeIssues]
        a: ConstrainedInt
        b: ConstrainedStr
        c: Union[ConstrainedInt, ConstrainedStr]
        d: Optional[ConstrainedInt]
        e: Optional[Union[ConstrainedInt, ConstrainedStr]]
        f: List[ConstrainedInt]
        g: Dict[ConstrainedInt, ConstrainedStr]

    ModelFactory.create_factory(Foo).build()  # type: ignore[type-var]


def test_build_v2_with_contrained_fields() -> None:
    from pydantic.fields import Field

    ConstrainedInt = Annotated[int, Field(ge=100, le=200)]
    ConstrainedStr = Annotated[str, Field(min_length=1, max_length=3)]

    class Foo(pydantic.BaseModel):  # pyright: ignore[reportGeneralTypeIssues]
        a: ConstrainedInt
        b: ConstrainedStr
        c: Union[ConstrainedInt, ConstrainedStr]
        d: Optional[ConstrainedInt]
        e: Optional[Union[ConstrainedInt, ConstrainedStr]]
        f: List[ConstrainedInt]
        g: Dict[ConstrainedInt, ConstrainedStr]

    ModelFactory.create_factory(Foo).build()
