from dataclasses import dataclass

import pytest

from polyfactory import ConfigurationError
from polyfactory.factories.base import DataclassFactory
from polyfactory.factories.pydantic_factory import ModelFactory
from polyfactory.field_meta import Null


def test_factory_raises_config_error_for_unsupported_model_with_supported_factory() -> None:
    @dataclass
    class DataclassModel:
        id: int

    with pytest.raises(ConfigurationError):

        class MyFactory1(ModelFactory):
            __model__ = DataclassModel

    class MyFactory2(DataclassFactory):
        __model__ = DataclassModel


def test_factory_raises_config_error_for_unsupported_model() -> None:
    with pytest.raises(ConfigurationError):

        class MyFactory(ModelFactory):
            __model__ = Null
