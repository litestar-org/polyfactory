from dataclasses import Field as DataclassField
from dataclasses import fields as get_dataclass_fields
from decimal import Decimal
from inspect import isclass
from typing import Any, ItemsView, Tuple, Type, TypeVar, Union, cast

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


def create_model_from_dataclass(
    dataclass: Type[DataclassProtocol],
) -> Type[BaseModel]:
    """
    Creates a a subclass of BaseModel from a given dataclass

    We are limited here because Pydantic does not perform proper field parsing when going this route -
    which requires we set the fields as required and not required independently.
    We currently do not handle deeply nested Any and Optional.
    """
    dataclass_fields: Tuple[DataclassField, ...] = get_dataclass_fields(dataclass)
    model = create_model("DataclassProxy", **{field.name: (field.type, ...) for field in dataclass_fields})  # type: ignore
    for field_name, model_field in model.__fields__.items():
        dataclass_field = [field for field in dataclass_fields if field.name == field_name][0]

        typing_string = repr(dataclass_field.type)
        if typing_string.startswith("typing.Optional") or typing_string == "typing.Any":
            model_field.required = False
            model_field.allow_none = True
        else:
            model_field.required = True
            model_field.allow_none = False
        setattr(model, field_name, model_field)
    return model


def get_model_fields(model: Union[Type[BaseModel], Type[DataclassProtocol]]) -> ItemsView[str, ModelField]:
    """
    A function to retrieve the fields of a given model.

    If the model passed is a dataclass, its converted to a pydantic model first.
    """
    if not is_pydantic_model(model):
        model = create_model_from_dataclass(dataclass=model)  # type: ignore
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
