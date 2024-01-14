import datetime as dt
import sys
from decimal import Decimal
from enum import Enum
from typing import Any, Dict, FrozenSet, Generic, List, NewType, Set, Tuple, Type, TypeVar, Union
from uuid import UUID

import msgspec
import pytest
from msgspec import Meta, Struct, structs
from typing_extensions import Annotated

from polyfactory.exceptions import ParameterException
from polyfactory.factories.msgspec_factory import MsgspecFactory


def test_is_supported_type() -> None:
    class Foo(Struct):
        ...

    assert MsgspecFactory.is_supported_type(Foo) is True


def test_is_supported_type_without_struct() -> None:
    class Foo:
        ...

    assert MsgspecFactory.is_supported_type(Foo) is False


def test_with_basic_types_without_constraints() -> None:
    class Foo(Struct):
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
        any_type: Any

    class FooFactory(MsgspecFactory[Foo]):
        __model__ = Foo

    foo = FooFactory.build()
    foo_dict = structs.asdict(foo)

    validated_foo = msgspec.convert(foo_dict, type=Foo)
    assert foo == validated_foo


def test_other_basic_types() -> None:
    # These types are tested separately since they can't be validated
    # using `convert`.
    # REFERENCE: https://github.com/jcrist/msgspec/issues/417

    class SampleEnum(Enum):
        FOO = "foo"
        BAR = "bar"

    class Foo(Struct):
        set_field: Set[int]
        frozenset_field: FrozenSet[int]
        enum_type: SampleEnum

    class FooFactory(MsgspecFactory[Foo]):
        __model__ = Foo

    foo = FooFactory.build()

    assert isinstance(foo.set_field, set)
    assert isinstance(foo.frozenset_field, frozenset)
    assert isinstance(foo.enum_type, SampleEnum)


def test_with_nested_struct() -> None:
    class Foo(Struct):
        int_field: int

    class Bar(Struct):
        int_field: int
        foo_field: Foo

    class BarFactory(MsgspecFactory[Bar]):
        __model__ = Bar

    bar = BarFactory.build()
    bar_dict = structs.asdict(bar)
    bar_dict["foo_field"] = structs.asdict(bar_dict["foo_field"])

    validated_bar = msgspec.convert(bar_dict, type=Bar)
    assert validated_bar == bar


def test_with_new_type() -> None:
    UnixName = NewType("UnixName", str)

    class User(Struct):
        name: UnixName
        groups: List[UnixName]

    class UserFactory(MsgspecFactory[User]):
        __model__ = User

    user = UserFactory.build()
    user_dict = structs.asdict(user)

    validated_user = msgspec.convert(user_dict, type=User)
    assert user == validated_user


def test_msgspec_types() -> None:
    class Foo(Struct):
        unset: msgspec.UnsetType
        ext: msgspec.msgpack.Ext
        raw: msgspec.Raw

    class FooFactory(MsgspecFactory[Foo]):
        __model__ = Foo

    foo = FooFactory.build()

    assert foo.unset == msgspec.UNSET
    assert isinstance(foo.ext, msgspec.msgpack.Ext)


@pytest.mark.skipif(sys.version_info < (3, 9), reason="flaky in 3.8")
def test_with_constraints() -> None:
    class Foo(Struct):
        int_field: Annotated[int, msgspec.Meta(ge=10, le=500, multiple_of=2)]
        float_field: Annotated[float, msgspec.Meta(ge=10, le=500, multiple_of=2)]
        str_field: Annotated[str, msgspec.Meta(min_length=100, max_length=500, pattern=r"\w")]
        bytes_field: Annotated[bytes, msgspec.Meta(min_length=100, max_length=500)]
        tuple_field: Annotated[Tuple[int, ...], msgspec.Meta(min_length=10, max_length=100)]
        list_field: Annotated[List[int], msgspec.Meta(min_length=10, max_length=100)]

    class FooFactory(MsgspecFactory[Foo]):
        __model__ = Foo

    foo = FooFactory.build()
    foo_dict = structs.asdict(foo)

    validated_foo = msgspec.convert(foo_dict, type=Foo)
    assert foo == validated_foo


@pytest.mark.skipif(sys.version_info < (3, 9), reason="flaky in 3.8")
def test_dict_constraints() -> None:
    class Foo(Struct):
        dict_field: Annotated[Dict[str, int], msgspec.Meta(min_length=1)]

    class FooFactory(MsgspecFactory[Foo]):
        __model__ = Foo

    foo = FooFactory.build()
    foo_dict = structs.asdict(foo)

    validated_foo = msgspec.convert(foo_dict, type=Foo)
    assert foo == validated_foo


@pytest.mark.skipif(sys.version_info < (3, 9), reason="flaky in 3.8")
@pytest.mark.parametrize("t", (dt.datetime, dt.time))
def test_datetime_constraints(t: Union[Type[dt.datetime], Type[dt.time]]) -> None:
    class Foo(Struct):
        date_field: Annotated[t, msgspec.Meta(tz=True)]  # type: ignore[valid-type]

    class FooFactory(MsgspecFactory[Foo]):
        __model__ = Foo

    with pytest.raises(ParameterException):
        _ = FooFactory.build()


def test_inheritence() -> None:
    class Foo(Struct):
        int_field: int

    class Bar(Foo):
        pass

    class BarFactory(MsgspecFactory[Bar]):
        __model__ = Bar

    bar = BarFactory.build()
    bar_dict = structs.asdict(bar)

    validated_bar = msgspec.convert(bar_dict, type=Bar)
    assert validated_bar == bar


def test_inheritence_with_generics() -> None:
    T = TypeVar("T")

    class Foo(Struct, Generic[T]):
        int_field: int
        generic_field: T

    class Bar(Foo[str]):
        pass

    class BarFactory(MsgspecFactory[Bar]):
        __model__ = Bar

    bar = BarFactory.build()
    bar_dict = structs.asdict(bar)

    validated_bar = msgspec.convert(bar_dict, type=Bar)
    assert validated_bar == bar


def test_sequence_with_constrained_item_types() -> None:
    ConstrainedInt = Annotated[int, Meta(ge=100, le=200)]

    class Foo(Struct):
        list_field: List[ConstrainedInt]
        tuple_field: Tuple[ConstrainedInt]
        variable_tuple_field: Tuple[ConstrainedInt, ...]
        set_field: Set[ConstrainedInt]

    class FooFactory(MsgspecFactory[Foo]):
        __model__ = Foo

    foo = FooFactory.build()
    validated_foo = msgspec.convert(structs.asdict(foo), Foo)

    assert validated_foo == foo


def test_mapping_with_constrained_item_types() -> None:
    ConstrainedInt = Annotated[int, Meta(ge=100, le=200)]
    ConstrainedStr = Annotated[str, Meta(min_length=1, max_length=3)]

    class Foo(Struct):
        dict_field = Dict[ConstrainedStr, ConstrainedInt]

    class FooFactory(MsgspecFactory[Foo]):
        __model__ = Foo

    foo = FooFactory.build()
    validated_foo = msgspec.convert(structs.asdict(foo), Foo)

    assert validated_foo == foo


def test_use_default_with_callable_default() -> None:
    class Foo(Struct):
        default_field: int = msgspec.field(default_factory=lambda: 10)

    class FooFactory(MsgspecFactory[Foo]):
        __model__ = Foo
        __use_defaults__ = True

    foo = FooFactory.build()

    assert foo.default_field == 10


def test_use_default_with_non_callable_default() -> None:
    class Foo(Struct):
        default_field: int = 10

    class FooFactory(MsgspecFactory[Foo]):
        __model__ = Foo
        __use_defaults__ = True

    foo = FooFactory.build()

    assert foo.default_field == 10
