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


def recursive_set_model_fields_required(model_field: ModelField) -> ModelField:
    """
    Traverse and update model_fields graph to all be required

    This is required because create_model exported from pydantic does not support required fields
    """
    model_field.required = True
    for index, sub_field in enumerate(model_field.sub_fields or []):
        model_field.sub_fields[index] = recursive_set_model_fields_required(model_field=sub_field)  # type: ignore
    return model_field


def get_model_fields(model: Union[Type[BaseModel], Type[DataclassProtocol]]) -> ItemsView[str, ModelField]:
    """
    A function to retrieve the fields of a given model.

    If the model passed is a dataclass, its converted to a pydantic model first.
    """
    if not is_pydantic_model(model):
        model_fields = fields(model)
        field_definitions = {field.name: (field.type, None) for field in model_fields}
        model = cast(Type[BaseModel], create_model("DataclassProxy", **field_definitions))  # type: ignore
        for field_name, field in model.__fields__.items():
            setattr(model, field_name, recursive_set_model_fields_required(model_field=field))
    return cast(Type[BaseModel], model).__fields__.items()


def is_union(model_field: ModelField) -> bool:
    """Determines whether the given model_field is type Union"""
    return repr(model_field.outer_type_).split("[")[0] == "typing.Union"


def is_any(model_field: ModelField) -> bool:
    """Determines whether the given model_field is type Any"""
    return model_field.type_ is Any or (
        hasattr(model_field.outer_type_, "_name")
        and getattr(model_field.outer_type_, "_name")
        and "Any" in getattr(model_field.outer_type_, "_name")
    )


def is_optional(model_field: ModelField) -> bool:
    """Determines whether the given model_field is type Optional"""
    return model_field.allow_none and not is_any(model_field=model_field) and not model_field.required
