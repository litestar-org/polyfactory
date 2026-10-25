from dataclasses import dataclass

from polyfactory.factories import DataclassFactory
from polyfactory.field_meta import FieldMeta


def test_model_fields_are_computed_once_per_factory() -> None:
    @dataclass
    class Foo:
        a: int
        b: list[int]

    calls = 0

    class FooFactory(DataclassFactory[Foo]):
        @classmethod
        def get_model_fields(cls) -> list[FieldMeta]:
            nonlocal calls
            calls += 1
            return super().get_model_fields()

    FooFactory.build()
    FooFactory.build()
    list(FooFactory.coverage())

    assert calls == 1


def test_factory_subclass_with_another_model_uses_its_own_fields() -> None:
    @dataclass
    class Foo:
        a: int

    @dataclass
    class Bar:
        b: str

    class FooFactory(DataclassFactory[Foo]):
        __model__ = Foo

    class BarFactory(FooFactory):
        __model__ = Bar  # type: ignore[assignment]

    FooFactory.build()

    assert isinstance(BarFactory.build(), Bar)
    assert isinstance(FooFactory.build(), Foo)
