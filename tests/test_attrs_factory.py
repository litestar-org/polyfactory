import datetime as dt
from decimal import Decimal
from enum import Enum
from typing import Any, Dict, Generic, List, Optional, Tuple, TypeVar, Union
from uuid import UUID

import attrs
import pytest
from attrs import asdict, define

from polyfactory.factories.attrs_factory import AttrsFactory

pytestmark = [pytest.mark.attrs]


def test_is_supported_type() -> None:
    @define
    class Foo: ...

    assert AttrsFactory.is_supported_type(Foo) is True


def test_is_supported_type_without_struct() -> None:
    class Foo: ...

    assert AttrsFactory.is_supported_type(Foo) is False


def test_with_basic_types_annotated() -> None:
    class SampleEnum(Enum):
        FOO = "foo"
        BAR = "bar"

    @define
    class Foo:
        bool_field: bool
        int_field: int
        float_field: float
        str_field: str
        bytse_field: bytes
        bytearray_field: bytearray
        tuple_field: Tuple[int, str]
        tuple_with_variadic_args: Tuple[int, ...]
        list_field: List[int]
        dict_field: Dict[str, int]
        datetime_field: dt.datetime
        date_field: dt.date
        time_field: dt.time
        uuid_field: UUID
        decimal_field: Decimal
        enum_type: SampleEnum
        any_type: Any

    class FooFactory(AttrsFactory[Foo]):
        __model__ = Foo

    foo = FooFactory.build()
    foo_dict = asdict(foo)

    assert foo == Foo(**foo_dict)


def test_with_basic_types_attrs_field() -> None:
    @define
    class Foo:
        bool_field = attrs.field(type=bool)  # pyright: ignore
        int_field = attrs.field(type=int)  # pyright: ignore
        float_field = attrs.field(type=float)  # pyright: ignore
        str_field = attrs.field(type=str)  # pyright: ignore
        bytes_field = attrs.field(type=bytes)  # pyright: ignore
        bytearray_field = attrs.field(type=bytearray)  # pyright: ignore
        tuple_field = attrs.field(type=Tuple[int, str])  # type: ignore
        tuple_with_variadic_args = attrs.field(type=Tuple[int, ...])  # type: ignore
        list_field = attrs.field(type=List[int])  # pyright: ignore
        dict_field = attrs.field(type=Dict[int, str])  # pyright: ignore
        datetime_field = attrs.field(type=dt.datetime)  # pyright: ignore
        date_field = attrs.field(type=dt.date)  # pyright: ignore
        time_field = attrs.field(type=dt.time)  # pyright: ignore
        uuid_field = attrs.field(type=UUID)  # pyright: ignore
        decimal_field = attrs.field(type=Decimal)  # pyright: ignore

    class FooFactory(AttrsFactory[Foo]):
        __model__ = Foo

    foo = FooFactory.build()
    foo_dict = asdict(foo)

    assert foo == Foo(**foo_dict)


def test_with_nested_attr_model() -> None:
    @define
    class Foo:
        int_field: int

    @define
    class Bar:
        int_field: int
        foo_field: Foo

    class BarFactory(AttrsFactory[Bar]):
        __model__ = Bar

    bar = BarFactory.build()
    bar_dict = asdict(bar, recurse=False)

    assert bar == Bar(**bar_dict)


def test_with_private_fields() -> None:
    @define
    class Foo:
        _private: int

    class FooFactory(AttrsFactory[Foo]):
        __model__ = Foo

    foo = FooFactory.build()

    assert foo == Foo(foo._private)


def test_with_aliased_fields() -> None:
    @define
    class Foo:
        aliased: int = attrs.field(alias="foo")

    class FooFactory(AttrsFactory[Foo]):
        __model__ = Foo

    foo = FooFactory.build()

    assert foo == Foo(foo.aliased)


def test_with_generics() -> None:
    T = TypeVar("T")

    @define
    class Foo(Generic[T]):
        x: T

    class FooFactory(AttrsFactory[Foo[str]]):
        __model__ = Foo

    foo = FooFactory.build()
    foo_dict = asdict(foo)

    assert foo == Foo(**foo_dict)


def test_with_inheritance() -> None:
    @define
    class Parent:
        int_field: int

    @define
    class Child:
        str_field: str

    class ChildFactory(AttrsFactory[Child]):
        __model__ = Child

    child = ChildFactory.build()
    child_dict = asdict(child)

    assert child == Child(**child_dict)


def test_with_stringified_annotations() -> None:
    @define
    class Foo:
        int_field: "int"

    class FooFactory(AttrsFactory[Foo]):
        __model__ = Foo

    foo = FooFactory.build()

    assert isinstance(foo.int_field, int)


def test_with_init_false() -> None:
    @define
    class Foo:
        foo: int = attrs.field(init=False)

    class FooFactory(AttrsFactory[Foo]):
        __model__ = Foo

    assert FooFactory.build()


def test_use_default_with_callable_default() -> None:
    @define
    class Foo:
        default_field: int = attrs.field(default=attrs.Factory(lambda: 10, takes_self=False))

    class FooFactory(AttrsFactory[Foo]):
        __model__ = Foo
        __use_defaults__ = True

    foo = FooFactory.build()

    assert foo.default_field == 10


def test_use_default_with_non_callable_default() -> None:
    @define
    class Foo:
        default_field: int = attrs.field(default=10)

    class FooFactory(AttrsFactory[Foo]):
        __model__ = Foo
        __use_defaults__ = True

    foo = FooFactory.build()

    assert foo.default_field == 10


def test_union_types() -> None:
    @define
    class A:
        a: Union[List[str], List[int]]
        b: Union[str, List[int]]
        c: List[Union[Tuple[int, int], Tuple[str, int]]]

    AFactory = AttrsFactory.create_factory(A)

    assert AFactory.build()


def test_collection_unions_with_models() -> None:
    @define
    class A:
        a: int

    @define
    class B:
        a: str

    @define
    class C:
        a: Union[List[A], List[B]]
        b: List[Union[A, B]]

    CFactory = AttrsFactory.create_factory(C)

    assert CFactory.build()


@pytest.mark.parametrize("allow_none", (True, False))
def test_optional_type(allow_none: bool) -> None:
    @define
    class A:
        a: Union[str, None]
        b: Optional[str]
        c: Optional[Union[str, int, List[int]]]

    class AFactory(AttrsFactory[A]):
        __model__ = A

        __allow_none_optionals__ = allow_none

    assert AFactory.build()
