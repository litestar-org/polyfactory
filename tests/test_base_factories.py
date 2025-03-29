from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Callable, Dict, NewType

import pytest
from typing_extensions import Annotated

from pydantic.main import BaseModel

from polyfactory.exceptions import ParameterException
from polyfactory.factories import DataclassFactory
from polyfactory.factories.base import BaseFactory
from polyfactory.factories.pydantic_factory import ModelFactory


def test_multiple_base_factories() -> None:
    class Foo:
        def __init__(self, value: str) -> None:
            self.value = value

    @dataclass
    class MyModelWithFoo:
        foo: Foo

    class FooDataclassFactory(DataclassFactory):
        __is_base_factory__ = True

        @classmethod
        def get_provider_map(cls) -> Dict[Any, Any]:
            return {Foo: lambda: Foo("foo"), **super().get_provider_map()}

    # noinspection PyUnusedLocal
    class DummyDataclassFactory(DataclassFactory):
        __is_base_factory__ = True

    @dataclass
    class MyModel:
        nested: MyModelWithFoo

    class MyFactory(FooDataclassFactory):
        __model__ = MyModel
        __base_factory_overrides__ = {MyModelWithFoo: FooDataclassFactory}

    MyFactory.build()


@pytest.mark.parametrize("override_BaseModel", [False, True])
def test_multiple_base_pydantic_factories(override_BaseModel: bool) -> None:
    class Foo:
        def __init__(self, value: str) -> None:
            self.value = value

    class MyModelWithFoo(BaseModel):
        foo: Foo

        class Config:
            arbitrary_types_allowed = True

    class FooModelFactory(ModelFactory):
        __is_base_factory__ = True

        @classmethod
        def get_provider_map(cls) -> Dict[Any, Any]:
            return {Foo: lambda: Foo("foo"), **super().get_provider_map()}

    # noinspection PyUnusedLocal
    class DummyModelFactory(ModelFactory):
        __is_base_factory__ = True

    class MyModel(BaseModel):
        nested: MyModelWithFoo

    class MyFactory(FooModelFactory):
        __model__ = MyModel
        if override_BaseModel:
            __base_factory_overrides__ = {BaseModel: FooModelFactory}
        else:
            __base_factory_overrides__ = {MyModelWithFoo: FooModelFactory}

    MyFactory.build()

    # XXX: remove the factory classes from _base_factories to prevent side-effects in other tests
    # see https://github.com/litestar-org/polyfactory/issues/198
    ModelFactory._base_factories.remove(FooModelFactory)
    ModelFactory._base_factories.remove(DummyModelFactory)


def test_create_factory_without_model_reuse_current_factory_model() -> None:
    @dataclass
    class Foo:
        pass

    factory = DataclassFactory.create_factory(model=Foo)
    sub_factory = factory.create_factory()

    assert sub_factory.__model__ == Foo


def test_create_factory_from_base_factory_without_providing_a_model_raises_error() -> None:
    with pytest.raises(TypeError):
        BaseFactory.create_factory()


def test_abstract_classes_are_ignored() -> None:
    @dataclass
    class Base(ABC):
        @abstractmethod
        def f(self) -> int: ...

    @dataclass
    class Concrete(Base):
        def f(self) -> int:
            return 1

    @dataclass
    class Model:
        single: Base

    class ModelFactory(DataclassFactory[Model]):
        @classmethod
        def get_provider_map(cls) -> Dict[type, Callable[[], Any]]:
            return {
                **super().get_provider_map(),
                Base: Concrete,
            }

    result = ModelFactory.build()
    assert isinstance(result, Model)
    assert isinstance(result.single, Concrete)

    with pytest.raises(ParameterException, match="Unsupported type: "):
        DataclassFactory.create_factory(Model).build()


AnnotatedType = Annotated[str, "foo"]
CustomNewType = NewType("CustomNewType", str)


def test_annotated_types_used_as_provider() -> None:
    @dataclass
    class Model:
        a: AnnotatedType
        b: CustomNewType

    class Factory(DataclassFactory[Model]):
        @classmethod
        def get_provider_map(cls) -> Dict[Any, Callable[[], Any]]:
            return {
                **super().get_provider_map(),
                AnnotatedType: lambda: "foo",
                CustomNewType: lambda: "bar",
            }

    result = Factory.build()
    assert result.a == "foo"
    assert result.b == "bar"

    result_coverage = list(Factory.coverage())
    assert len(result_coverage) == 1
    assert result_coverage[0].a == "foo"
    assert result_coverage[0].b == "bar"
