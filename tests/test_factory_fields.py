from typing import Optional

import pytest
from pydantic import BaseModel

from pydantic_factories import ModelFactory, Use
from pydantic_factories.exceptions import MissingBuildKwargError
from pydantic_factories.fields import Ignore, Require


def test_use():
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
        my_class = Use(cb=MyClass.builder, name=default_name)

    result = MyFactory.build()
    assert result.my_class.name == default_name


def test_sub_factory():
    default_name = "Moishe Zuchmir"

    class FirstModel(BaseModel):
        name: str

    class SecondModel(BaseModel):
        first_model: FirstModel

    class MyFactory(ModelFactory):
        __model__ = SecondModel
        first_model = Use(cb=ModelFactory.create_factory(FirstModel).build, name=default_name)

    result = MyFactory.build()
    assert result.first_model.name == default_name


def test_build_kwarg():
    class MyModel(BaseModel):
        name: str

    class MyFactory(ModelFactory):
        __model__ = MyModel
        name = Require()

    with pytest.raises(MissingBuildKwargError):
        MyFactory.build()

    assert MyFactory.build(name="moishe").name == "moishe"


def test_ignored():
    class MyModel(BaseModel):
        name: Optional[str]

    class MyFactory(ModelFactory):
        __model__ = MyModel
        name = Ignore()

    assert MyFactory.build().name is None
