from typing import Any

from pydantic import BaseModel
from pydantic.fields import ModelField

from pydantic_factories.factory import ModelFactory
from pydantic_factories.utils import random

try:  # pragma: no cover
    from ormar import Model
except ImportError:  # pragma: no cover
    Model = BaseModel


# FIX: once ormar updates to pydantic 1.9.0, uncomment the tests and return this to the dev dependencies


class OrmarModelFactory(ModelFactory[Model]):  # pragma: no cover
    @classmethod
    def get_field_value(cls, model_field: ModelField) -> Any:
        """
        We need to handle here both choices and the fact that ormar sets values to be optional
        """
        model_field.required = True
        if hasattr(model_field.field_info, "choices") and len(model_field.field_info.choices) > 0:  # type: ignore
            return random.choice(list(model_field.field_info.choices))  # type: ignore
        return super().get_field_value(model_field=model_field)
