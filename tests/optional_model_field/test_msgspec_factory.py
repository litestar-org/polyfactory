import msgspec
from msgspec import Struct, structs

from polyfactory.factories.msgspec_factory import MsgspecFactory


def test_with_nested_struct() -> None:
    class Foo(Struct):
        int_field: int

    class Bar(Struct):
        int_field: int
        foo_field: Foo

    class BarFactory(MsgspecFactory[Bar]):
        ...

    assert getattr(BarFactory, "__model__") is Bar

    bar: Bar = BarFactory.build()
    bar_dict = structs.asdict(bar)
    bar_dict["foo_field"] = structs.asdict(bar_dict["foo_field"])

    validated_bar = msgspec.convert(bar_dict, type=Bar)
    assert validated_bar == bar
