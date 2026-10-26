from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Generic, TypeVar

import pytest

import pydantic
from pydantic import BaseModel, ValidationError

from polyfactory.exceptions import ParameterException
from polyfactory.factories.base import BaseFactory
from polyfactory.factories.dataclass_factory import DataclassFactory
from polyfactory.factories.pydantic_factory import ModelFactory


def test_provider_map() -> None:
    provider_map = BaseFactory.get_provider_map()
    provider_map.pop(Any)

    for type_, handler in provider_map.items():
        value = handler()
        assert isinstance(value, type_)


def test_provider_map_with_any() -> None:
    @dataclass
    class Foo:
        foo: Any

    class FooFactory(DataclassFactory[Foo]):
        @classmethod
        def get_provider_map(cls) -> dict[Any, Callable[[], Any]]:
            provider_map = super().get_provider_map()
            provider_map[Any] = lambda: "any"

            return provider_map

    foo = FooFactory.build()

    assert foo.foo == "any"

    coverage_result = list(FooFactory.coverage())
    assert all(result.foo == "any" for result in coverage_result)


def test_provider_map_with_typevar() -> None:
    T = TypeVar("T")

    @dataclass
    class Foo(Generic[T]):
        foo: T

    class FooFactory(DataclassFactory[Foo]):
        @classmethod
        def get_provider_map(cls) -> dict[Any, Callable[[], Any]]:
            provider_map = super().get_provider_map()
            provider_map[T] = lambda: "any"

            return provider_map

    foo = FooFactory.build()
    assert foo.foo == "any"

    coverage_result = list(FooFactory.coverage())
    assert all(result.foo == "any" for result in coverage_result)


def test_provider_map_takes_priority_over_factory_type() -> None:
    """Custom providers should take precedence over built-in factory type resolution."""

    @dataclass
    class Inner:
        value: str

    @dataclass
    class Outer:
        inner: Inner

    sentinel = Inner(value="from_provider")

    class OuterFactory(DataclassFactory[Outer]):
        @classmethod
        def get_provider_map(cls) -> dict[Any, Callable[[], Any]]:
            return {Inner: lambda: sentinel, **super().get_provider_map()}

    assert OuterFactory.build().inner is sentinel
    assert all(result.inner is sentinel for result in OuterFactory.coverage())


def test_provider_map_takes_priority_over_pydantic_factory_type() -> None:
    """Custom providers should take precedence for Pydantic model fields."""

    class InnerModel(BaseModel):
        value: str

    class OuterModel(BaseModel):
        inner: InnerModel

    class OuterFactory(ModelFactory[OuterModel]):
        @classmethod
        def get_provider_map(cls) -> dict[Any, Callable[[], Any]]:
            return {InnerModel: lambda: InnerModel(value="from_provider"), **super().get_provider_map()}

    assert OuterFactory.build().inner.value == "from_provider"
    assert all(result.inner.value == "from_provider" for result in OuterFactory.coverage())


def test_add_custom_provider() -> None:
    class CustomType:
        def __init__(self, _: Any) -> None:
            pass

    @dataclass
    class Foo:
        foo: CustomType

    FooFactory = DataclassFactory.create_factory(Foo)

    with pytest.raises(ParameterException):
        FooFactory.build()

    BaseFactory.add_provider(CustomType, lambda: CustomType("custom"))

    # after adding the provider, nothing should raise!
    assert FooFactory.build()


def test_provider_map_is_built_once_per_build() -> None:
    @dataclass
    class Foo:
        a: int
        b: list[int]

    calls = 0

    class FooFactory(DataclassFactory[Foo]):
        @classmethod
        def get_provider_map(cls) -> dict[Any, Callable[[], Any]]:
            nonlocal calls
            calls += 1
            return super().get_provider_map()

    FooFactory.build()
    assert calls == 1

    list(FooFactory.coverage())
    assert calls == 2


def test_nested_factory_uses_its_own_provider_map() -> None:
    @dataclass
    class Inner:
        b: int

    @dataclass
    class Outer:
        a: int
        inner: Inner

    class InnerFactory(DataclassFactory[Inner]):
        @classmethod
        def get_provider_map(cls) -> dict[Any, Callable[[], Any]]:
            return {**super().get_provider_map(), int: lambda: 2}

    class OuterFactory(DataclassFactory[Outer]):
        inner = InnerFactory

        @classmethod
        def get_provider_map(cls) -> dict[Any, Callable[[], Any]]:
            return {**super().get_provider_map(), int: lambda: 1}

    outer = OuterFactory.build()

    assert outer.a == 1
    assert outer.inner.b == 2


@pytest.mark.parametrize("use_coverage", [False, True])
@pytest.mark.parametrize("use_registry", [False, True])
def test_custom_enum_provider_for_empty_enum(
    monkeypatch: pytest.MonkeyPatch, use_coverage: bool, use_registry: bool
) -> None:
    """Explicit providers populate empty enum bases, including nested mapping keys."""

    class BaseEnum(Enum):
        pass

    class ConcreteEnum(BaseEnum):
        FIRST = 1
        SECOND = 2

    @dataclass
    class Model:
        value: BaseEnum
        mapping: dict[BaseEnum, int]

    class ModelFactory(DataclassFactory[Model]):
        @classmethod
        def get_provider_map(cls) -> dict[Any, Callable[[], Any]]:
            providers = super().get_provider_map()
            if not use_registry:
                providers[BaseEnum] = lambda: ConcreteEnum.FIRST
            return providers

    if use_registry:
        monkeypatch.setattr(BaseFactory, "_providers", BaseFactory._providers.copy())
        ModelFactory.add_provider(BaseEnum, lambda: ConcreteEnum.FIRST)

    results = list(ModelFactory.coverage()) if use_coverage else [ModelFactory.build()]

    assert len(results) == 1
    assert results[0].value is ConcreteEnum.FIRST
    assert set(results[0].mapping) == {ConcreteEnum.FIRST}


@pytest.mark.parametrize("use_coverage", [False, True])
def test_custom_enum_provider_for_populated_enum(use_coverage: bool) -> None:
    """An explicit provider also overrides member generation for populated enums."""

    class Choice(Enum):
        FIRST = 1
        SECOND = 2

    @dataclass
    class Model:
        value: Choice

    class ModelFactory(DataclassFactory[Model]):
        __random_seed__ = 0

        @classmethod
        def get_provider_map(cls) -> dict[Any, Callable[[], Any]]:
            return {**super().get_provider_map(), Choice: lambda: Choice.FIRST}

    results = list(ModelFactory.coverage()) if use_coverage else [ModelFactory.build()]

    assert len(results) == 1
    assert results[0].value is Choice.FIRST


def test_default_enum_provider_fallback() -> None:
    """Unconfigured enum fields retain random member generation and full coverage."""

    class Choice(Enum):
        FIRST = 1
        SECOND = 2

    @dataclass
    class Model:
        value: Choice

    class ModelFactory(DataclassFactory[Model]):
        pass

    assert ModelFactory.build().value in Choice
    assert [result.value for result in ModelFactory.coverage()] == list(Choice)


@pytest.mark.parametrize("use_coverage", [False, True])
def test_custom_enum_provider_for_pydantic_model(use_coverage: bool) -> None:
    """Providers populate empty enum fields before the model validates them."""

    class BaseEnum(Enum):
        pass

    class ConcreteEnum(BaseEnum):
        FIRST = 1

    class Model(BaseModel):
        value: BaseEnum
        mapping: dict[BaseEnum, int]

    provided_values: list[BaseEnum] = []

    def provide_enum() -> BaseEnum:
        provided_values.append(ConcreteEnum.FIRST)
        return ConcreteEnum.FIRST

    class EnumFactory(ModelFactory[Model]):
        @classmethod
        def get_provider_map(cls) -> dict[Any, Callable[[], Any]]:
            return {**super().get_provider_map(), BaseEnum: provide_enum}

    if pydantic.VERSION.startswith("1"):
        with pytest.raises(ValidationError) as exc_info:
            list(EnumFactory.coverage()) if use_coverage else EnumFactory.build()

        errors = exc_info.value.errors()
        assert len(errors) == 2
        assert {error["loc"] for error in errors} == {("value",), ("mapping", "__key__")}
        assert all("no members" in error["msg"] for error in errors)
        assert len(provided_values) >= 2
        assert all(value is ConcreteEnum.FIRST for value in provided_values)
        return

    results = list(EnumFactory.coverage()) if use_coverage else [EnumFactory.build()]

    assert len(results) == 1
    assert results[0].value is ConcreteEnum.FIRST
    assert set(results[0].mapping) == {ConcreteEnum.FIRST}


@pytest.mark.parametrize("use_coverage", [False, True])
def test_custom_enum_provider_for_populated_pydantic_enum(use_coverage: bool) -> None:
    """Pydantic v1 and v2 accept custom members and nested keys of populated enums."""

    class Choice(Enum):
        FIRST = 1
        SECOND = 2

    class Model(BaseModel):
        value: Choice
        mapping: dict[Choice, int]

    class EnumFactory(ModelFactory[Model]):
        __random_seed__ = 0

        @classmethod
        def get_provider_map(cls) -> dict[Any, Callable[[], Any]]:
            return {**super().get_provider_map(), Choice: lambda: Choice.FIRST}

    results = list(EnumFactory.coverage()) if use_coverage else [EnumFactory.build()]

    assert len(results) == 1
    assert results[0].value is Choice.FIRST
    assert set(results[0].mapping) == {Choice.FIRST}
