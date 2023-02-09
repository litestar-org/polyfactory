from dataclasses import Field as DataclassField
from dataclasses import fields as get_dataclass_fields
from decimal import Decimal
from inspect import isclass
from typing import TYPE_CHECKING, Any, Optional, Tuple, Type, TypeVar, cast

from pydantic import BaseModel, create_model
from pydantic.generics import GenericModel
from pydantic.utils import almost_equal_floats

T = TypeVar("T", int, float, Decimal)

if TYPE_CHECKING:
    from typing import NewType

    from pydantic.fields import ModelField
    from typing_extensions import TypeGuard

    from pydantic_factories.protocols import DataclassProtocol


def passes_pydantic_multiple_validator(value: T, multiple_of: T) -> bool:
    """A function that determines whether a given value passes the pydantic multiple_of validation."""
    if multiple_of == 0:
        return True
    mod = float(value) / float(multiple_of) % 1
    return almost_equal_floats(mod, 0.0) or almost_equal_floats(mod, 1.0)


def is_multiply_of_multiple_of_in_range(minimum: Optional[T], maximum: Optional[T], multiple_of: T) -> bool:
    """Determines if at least one multiply of `multiple_of` lies in the given range."""
    # if the range has infinity on one of its ends then infinite number of multipliers
    # can be found within the range
    if minimum is None or maximum is None:
        return True

    # if we were given floats and multiple_of is really close to zero then it doesn't make sense
    # to continue trying to check the range
    if isinstance(minimum, float) and minimum / multiple_of in [float("+inf"), float("-inf")]:
        return False

    multiplier = round(minimum / multiple_of)
    step = 1 if multiple_of > 0 else -1
    # since rounding can go either up or down we may end up in a situation when
    # minimum is less or equal to `multiplier * multiple_of`
    # or when it is greater than `multiplier * multiple_of`
    # (in this case minimum is less than `(multiplier + 1)* multiple_of`). So we need to check
    # that any of two values is inside the given range. ASCII graphic below explain this
    #
    #                minimum
    # -----------------+-------+-----------------------------------+----------------------------
    #             multiplier * multiple_of        (multiplier + 1) * multiple_of
    #
    #
    #                                minimum
    # -------------------------+--------+--------------------------+----------------------------
    #             multiplier * multiple_of        (multiplier + 1) * multiple_of
    #
    # since `multiple_of` can be a negative number adding +1 to `multiplier` drives `(multiplier + 1) * multiple_of``
    # away from `minumum` to the -infinity. It looks like this:
    #                                                                               minimum
    # -----------------------+--------------------------------+------------------------+--------
    #       (multiplier + 1) * multiple_of        (multiplier) * multiple_of
    #
    # so for negative `multiple_of` we want to subtract 1 from multiplier
    for multiply in [multiplier * multiple_of, (multiplier + step) * multiple_of]:
        multiply_float = float(multiply)
        if (
            almost_equal_floats(multiply_float, float(minimum))
            or almost_equal_floats(multiply_float, float(maximum))
            or minimum < multiply < maximum
        ):
            return True

    return False


def is_pydantic_model(value: Any) -> "TypeGuard[Type[BaseModel]]":
    """A function to determine if a given value is a subclass of BaseModel."""
    try:
        return isclass(value) and issubclass(value, (BaseModel, GenericModel))
    except TypeError:  # pragma: no cover
        # isclass(value) returns True for python 3.9+ typings such as list[str] etc.
        # this raises a TypeError in issubclass, and so we need to handle it.
        return False


def set_model_field_to_required(model_field: "ModelField") -> "ModelField":
    """recursively sets the model_field and all sub_fields as required."""
    model_field.required = True
    if model_field.sub_fields:
        for index, sub_field in enumerate(model_field.sub_fields):
            model_field.sub_fields[index] = set_model_field_to_required(model_field=sub_field)
    return model_field


def create_model_from_dataclass(
    dataclass: Type["DataclassProtocol"],
) -> Type[BaseModel]:
    """Creates a subclass of BaseModel from a given dataclass.

    We are limited here because Pydantic does not perform proper field
    parsing when going this route - which requires we set the fields as
    required and not required independently. We currently do not handle
    deeply nested Any and Optional.
    """
    dataclass_fields: Tuple[DataclassField, ...] = get_dataclass_fields(dataclass)  # pyright: ignore
    model = create_model(dataclass.__name__, **{field.name: (field.type, ...) for field in dataclass_fields})  # type: ignore
    for field_name, model_field in model.__fields__.items():
        dataclass_field = [field for field in dataclass_fields if field.name == field_name][0]
        typing_string = repr(dataclass_field.type)
        model_field = set_model_field_to_required(model_field=model_field)
        if typing_string.startswith("typing.Optional") or typing_string == "typing.Any":
            model_field.required = False
            model_field.allow_none = True
            model_field.default = None
        else:
            model_field.required = True
            model_field.allow_none = False
        setattr(model, field_name, model_field)
    return cast("Type[BaseModel]", model)


def is_union(model_field: "ModelField") -> bool:
    """Determines whether the given model_field is type Union."""
    field_type_repr = repr(model_field.outer_type_)
    if field_type_repr.startswith("typing.Union[") or ("|" in field_type_repr) or model_field.discriminator_key:
        return True
    return False


def is_any(model_field: "ModelField") -> bool:
    """Determines whether the given model_field is type Any."""
    type_name = cast("Any", getattr(model_field.outer_type_, "_name", None))
    return model_field.type_ is Any or (type_name is not None and "Any" in type_name)


def is_optional(model_field: "ModelField") -> bool:
    """Determines whether the given model_field is type Optional."""
    return model_field.allow_none and not is_any(model_field=model_field) and not model_field.required


def is_literal(model_field: "ModelField") -> bool:
    """Determines whether a given model_field is a Literal type."""
    return "typing.Literal" in repr(model_field.outer_type_) or "typing_extensions.Literal" in repr(
        model_field.outer_type_
    )


def is_new_type(value: Any) -> "TypeGuard[Type[NewType]]":
    """A function to determine if a given value is of NewType."""
    # we have to use hasattr check since in Python 3.9 and below NewType is just a function
    return hasattr(value, "__supertype__")


def unwrap_new_type_if_needed(value: Type[Any]) -> Type[Any]:
    """Returns base type if given value is a type derived with NewType.

    Otherwise it returns value untouched.
    """
    unwrap = value
    while is_new_type(unwrap):
        unwrap = unwrap.__supertype__

    return unwrap
