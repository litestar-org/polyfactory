import datetime as dt
from decimal import Decimal
from enum import Enum
from typing import Any, Dict, List, Tuple
from uuid import UUID

import pytest
from attrs import asdict, define

from polyfactory.factories.attrs_factory import AttrsFactory

pytestmark = [pytest.mark.attrs]


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
        ...

    assert getattr(FooFactory, "__model__") is Foo

    foo: Foo = FooFactory.build()
    foo_dict = asdict(foo)

    assert foo == Foo(**foo_dict)
