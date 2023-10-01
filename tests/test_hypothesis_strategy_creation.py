import msgspec
from hypothesis import given
from msgspec import Struct
from msgspec.structs import asdict

from polyfactory.factories.msgspec_factory import MsgspecFactory


def test_without_constraints() -> None:
    class Foo(Struct):
        int_field: int
        str_field: str

    foo_st = MsgspecFactory.create_factory(Foo).build_hypothesis_strategy()

    @given(foo_st)
    def test_foo(foo: Foo) -> None:
        _ = msgspec.convert(asdict(foo), type=Foo)

    test_foo()
