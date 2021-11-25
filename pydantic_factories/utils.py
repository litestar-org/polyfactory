from dataclasses import fields
from decimal import Decimal
from inspect import isclass
from typing import Any, ItemsView, Type, TypeVar, Union, cast

from pydantic import BaseModel, create_model
from pydantic.fields import ModelField
from pydantic.utils import almost_equal_floats

from pydantic_factories.protocols import DataclassProtocol

T = TypeVar("T", int, float, Decimal)


def passes_pydantic_multiple_validator(value: T, multiple_of: T) -> bool:
    """A function that determines whether a given value passes the pydantic multiple_of validation"""
    if multiple_of == 0:
        return True
    mod = float(value) / float(multiple_of) % 1
    return almost_equal_floats(mod, 0.0) or almost_equal_floats(mod, 1.0)


def is_pydantic_model(value: Any) -> bool:
    """A function to determine if a given value is a subclass of BaseModel"""
    try:
        return isclass(value) and issubclass(value, BaseModel)
    except TypeError:  # pragma: no cover
        # isclass(value) returns True for python 3.9+ typings such as list[str] etc.
        # this raises a TypeError in issubclass, and so we need to handle it.
        return False


def get_model_fields(model: Union[Type[BaseModel], Type[DataclassProtocol]]) -> ItemsView[str, ModelField]:
    """
    A function to retrieve the fields of a given model.

    If the model passed is a dataclass, its converted to a pydantic model first.
    """
    if not is_pydantic_model(model):
        field_definitions = {field.name: (field.type, None) for field in fields(model)}
        model = create_model("DataclassProxy", **field_definitions)  # type: ignore
    return cast(Type[BaseModel], model).__fields__.items()
