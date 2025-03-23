import random
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, ClassVar, List, Optional, Union

import pytest

from pydantic import BaseModel

from polyfactory.decorators import post_generated
from polyfactory.exceptions import (
    ConfigurationException,
    MissingBuildKwargException,
    MissingParamException,
    ParameterException,
)
from polyfactory.factories.dataclass_factory import DataclassFactory
from polyfactory.factories.pydantic_factory import ModelFactory
from polyfactory.field_meta import Null
from polyfactory.fields import Ignore, Param, PostGenerated, Require, Use


def test_use() -> None:
    class MyClass:
        name: str

        @classmethod
        def builder(cls, name: str) -> "MyClass":
            instance = MyClass()
            instance.name = name
            return instance

    default_name = "Moishe Zuchmir"

    class MyModel(BaseModel):
        my_class: MyClass

        class Config:
            arbitrary_types_allowed = True

    class MyFactory(ModelFactory):
        __model__ = MyModel
        my_class = Use(fn=MyClass.builder, name=default_name)

    result = MyFactory.build()
    assert result.my_class.name == default_name


def test_sub_factory() -> None:
    default_name = "Moishe Zuchmir"

    class FirstModel(BaseModel):
        name: str

    class SecondModel(BaseModel):
        first_model: FirstModel

    class MyFactory(ModelFactory):
        __model__ = SecondModel
        first_model = Use(fn=ModelFactory.create_factory(FirstModel).build, name=default_name)

    result = MyFactory.build()
    assert result.first_model.name == default_name


def test_build_kwarg() -> None:
    class MyModel(BaseModel):
        name: str

    class MyFactory(ModelFactory):
        __model__ = MyModel
        name = Require()

    with pytest.raises(MissingBuildKwargException):
        MyFactory.build()

    assert MyFactory.build(name="moishe").name == "moishe"


def test_ignored() -> None:
    class MyModel(BaseModel):
        name: Optional[str] = None

    class MyFactory(ModelFactory):
        __model__ = MyModel

        name = Ignore()

    assert MyFactory.build().name is None


@pytest.mark.parametrize(
    "value,is_callable,kwargs",
    [
        (None, False, {}),
        (1, False, {}),
        ("foo", False, {}),
        (lambda value: value, True, {}),
        (lambda value1, value2: value1 + value2, True, {}),
        (lambda: "foo", True, {}),
        (lambda: "foo", True, {"value": 3}),
    ],
)
def test_param_init(value: Any, is_callable: bool, kwargs: dict[str, Any]) -> None:
    param = Param(value, is_callable, **kwargs)  # type: ignore
    assert isinstance(param, Param)
    assert param.param == value
    assert param.is_callable == is_callable
    assert param.kwargs == kwargs


@pytest.mark.parametrize(
    "value,is_callable,kwargs",
    [
        (None, True, {}),
        (1, True, {}),
        ("foo", True, {}),
        (Null, False, {"value": 3}),
        (1, False, {"value": 3}),
    ],
)
def test_param_init_error(value: Any, is_callable: bool, kwargs: dict[str, Any]) -> None:
    with pytest.raises(
        ParameterException,
    ):
        Param(value, is_callable, **kwargs)


@pytest.mark.parametrize(
    "initval,is_cabllable,initkwargs,buildval,buildkwargs,outcome",
    [
        (None, False, {}, Null, {}, None),
        (1, False, {}, 2, {}, 2),
        ("foo", False, {}, Null, {}, "foo"),
        (lambda value: value, True, {}, lambda value: value + 1, {"value": 3}, 4),
        (lambda value1, value2: value1 + value2, True, {"value1": 2}, Null, {"value2": 1}, 3),
        (lambda: "foo", True, {}, Null, {}, "foo"),
    ],
)
def test_param_to_value(
    initval: Any,
    is_cabllable: bool,
    initkwargs: dict[str, Any],
    buildval: Any,
    buildkwargs: dict[str, Any],
    outcome: Any,
) -> None:
    assert Param(initval, is_cabllable, **initkwargs).to_value(buildval, **buildkwargs) == outcome


@pytest.mark.parametrize(
    "initval,is_cabllable,initkwargs,buildval,buildkwargs,exc",
    [
        (Null, False, {}, Null, {}, MissingParamException),
        (Null, True, {}, 1, {}, TypeError),
    ],
)
def test_param_to_value_exception(
    initval: Any,
    is_cabllable: bool,
    initkwargs: dict[str, Any],
    buildval: Any,
    buildkwargs: dict[str, Any],
    exc: type[Exception],
) -> None:
    with pytest.raises(exc):
        Param(initval, is_cabllable, **initkwargs).to_value(buildval, **buildkwargs)


def test_param_from_factory() -> None:
    value: int = 3

    class MyModel(BaseModel):
        description: str

    class MyFactory(ModelFactory):
        __model__ = MyModel
        length = Param[int](value)

        @post_generated
        @classmethod
        def description(cls, length: int) -> str:
            return "abcd"[:length]

    result = MyFactory.build()
    assert result.description == "abc"


def test_param_from_kwargs() -> None:
    value: int = 3

    class MyModel(BaseModel):
        description: str

    class MyFactory(ModelFactory):
        __model__ = MyModel
        length = Param[int]()

        @post_generated
        @classmethod
        def description(cls, length: int) -> str:
            return "abcd"[:length]

    result = MyFactory.build(length=value)
    assert result.description == "abc"


def test_param_from_kwargs_missing() -> None:
    class MyModel(BaseModel):
        description: str

    class MyFactory(ModelFactory):
        __model__ = MyModel
        length = Param[int]()

        @post_generated
        @classmethod
        def description(cls, length: int) -> str:
            return "abcd"[:length]

    with pytest.raises(MissingBuildKwargException):
        MyFactory.build()


def test_callable_param_from_factory() -> None:
    class MyModel(BaseModel):
        description: str

    class MyFactory(ModelFactory):
        __model__ = MyModel
        length = Param(lambda value: value, is_callable=True, value=3)

        @post_generated
        @classmethod
        def description(cls, length: int) -> str:
            return "abcd"[:length]

    result = MyFactory.build()
    assert result.description == "abc"


def test_callable_param_from_kwargs() -> None:
    value1: int = 2
    value2: int = 1

    class MyModel(BaseModel):
        description: str

    class MyFactory(ModelFactory):
        __model__ = MyModel
        length = Param[int](is_callable=True, value1=value1, value2=value2)

        @post_generated
        @classmethod
        def description(cls, length: int) -> str:
            return "abcd"[:length]

    result = MyFactory.build(length=lambda value1, value2: value1 + value2)
    assert result.description == "abcd"[: value1 + value2]


def test_param_name_overlaps_model_field() -> None:
    class MyModel(BaseModel):
        name: str
        other: int

    with pytest.raises(ConfigurationException) as exc:

        class MyFactory(ModelFactory):
            __model__ = MyModel
            name = Param[str]("foo")
            other = 1

        assert "name" in str(exc)
        assert "other" not in str(exc)


def test_post_generation() -> None:
    random_delta = timedelta(days=random.randint(0, 12), seconds=random.randint(13, 13000))

    def add_timedelta(name: str, values: Any, **kwargs: Any) -> datetime:
        assert name == "to_dt"
        assert "from_dt" in values
        assert isinstance(values["from_dt"], datetime)
        return values["from_dt"] + random_delta

    def decide_long(name: str, values: Any, **kwargs: Any) -> bool:
        assert name == "is_long"
        assert "from_dt" in values
        assert "to_dt" in values
        assert "threshold" in kwargs
        assert isinstance(values["from_dt"], datetime)
        assert isinstance(values["to_dt"], datetime)
        difference = values["to_dt"] - values["from_dt"]
        return difference.days > kwargs["threshold"]  # type: ignore

    def make_caption(name: str, values: Any, **kwargs: Any) -> str:
        assert name == "caption"
        assert "is_long" in values
        return "this was really long for me" if values["is_long"] else "just this"

    class MyModel(BaseModel):
        from_dt: datetime
        to_dt: datetime
        is_long: bool
        caption: str

    class MyFactory(ModelFactory):
        __model__ = MyModel
        to_dt = PostGenerated(add_timedelta)
        is_long = PostGenerated(decide_long, threshold=1)
        caption = PostGenerated(make_caption)

    result = MyFactory.build()
    assert result.to_dt - result.from_dt == random_delta
    assert result.is_long == (random_delta.days > 1)
    if result.is_long:
        assert result.caption == "this was really long for me"
    else:
        assert result.caption == "just this"


def test_post_generation_classmethod() -> None:
    class MyModel(BaseModel):
        from_dt: datetime
        to_dt: datetime
        is_long: bool
        caption: str

    class MyFactory(ModelFactory):
        __model__ = MyModel

        random_delta: timedelta

        @post_generated
        @classmethod
        def to_dt(cls, from_dt: datetime) -> datetime:
            # save it to cls for test purposes only
            cls.random_delta = timedelta(days=cls.__random__.randint(0, 12), seconds=cls.__random__.randint(13, 13000))
            return from_dt + cls.random_delta

        @post_generated
        @classmethod
        def is_long(cls, from_dt: datetime, to_dt: datetime) -> bool:
            return (to_dt - from_dt).days > 1

        @post_generated
        @classmethod
        def caption(cls, is_long: bool) -> str:
            return "this was really long for me" if is_long else "just this"

    result = MyFactory.build()
    assert result.to_dt - result.from_dt == MyFactory.random_delta
    assert result.is_long == (MyFactory.random_delta.days > 1)
    if result.is_long:
        assert result.caption == "this was really long for me"
    else:
        assert result.caption == "just this"


@pytest.mark.parametrize(
    "factory_field",
    [
        Use(lambda: "foo"),
        PostGenerated(lambda: "foo"),
        Require(),
        Ignore(),
    ],
)
def test_non_existing_model_fields_does_not_raise_by_default(
    factory_field: Union[Use, PostGenerated, Require, Ignore],
) -> None:
    class NoFieldModel(BaseModel):
        pass

    ModelFactory.create_factory(NoFieldModel, bases=None, unknown_field=factory_field)


@pytest.mark.parametrize(
    "factory_field",
    [
        Use(lambda: "foo"),
        PostGenerated(lambda: "foo"),
        Require(),
        Ignore(),
    ],
)
def test_non_existing_model_fields_raises_with__check__model__(
    factory_field: Union[Use, PostGenerated, Require, Ignore],
) -> None:
    class NoFieldModel(BaseModel):
        pass

    with pytest.raises(
        ConfigurationException,
        match="unknown_field is declared on the factory NoFieldModelFactory but it is not part of the model NoFieldModel",
    ):
        ModelFactory.create_factory(NoFieldModel, bases=None, __check_model__=True, unknown_field=factory_field)


def test_mutable_defaults() -> None:
    @dataclass
    class A:
        a: List[str]

    class AFactory(DataclassFactory[A]):
        a: ClassVar[List[str]] = []

    AFactory.build().a.append("a")
    assert AFactory.build().a == []

    next(iter(AFactory.coverage())).a.append("value")
    assert next(iter(AFactory.coverage())).a == []
