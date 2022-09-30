import random
from typing import TYPE_CHECKING, Any, Union

from pydantic import BaseModel

from pydantic_factories.factory import ModelFactory
from pydantic_factories.utils import is_pydantic_model, is_union

try:
    from ormar import Model
except ImportError:
    Model = BaseModel  # type: ignore

if TYPE_CHECKING:
    from pydantic.fields import ModelField


class OrmarModelFactory(ModelFactory[Model]):  # pragma: no cover
    @classmethod
    def get_field_value(cls, model_field: "ModelField", field_parameters: Union[dict, list, None] = None) -> Any:
        """We need to handle here both choices and the fact that ormar sets
        values to be optional."""

        model_field.required = True
        # check if this is a RelationShip field
        if (
            is_union(model_field=model_field)
            and model_field.sub_fields
            and any("PkOnly" in sf.name for sf in model_field.sub_fields)
        ):
            return cls.get_field_value(
                model_field=[sf for sf in model_field.sub_fields if is_pydantic_model(sf.outer_type_)][0],
                field_parameters=field_parameters,
            )
        if getattr(model_field.field_info, "choices", False):
            return random.choice(list(model_field.field_info.choices))  # type: ignore
        return super().get_field_value(model_field=model_field, field_parameters=field_parameters)
