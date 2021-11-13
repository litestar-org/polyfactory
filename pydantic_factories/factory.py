from datetime import date, datetime, time
from decimal import Decimal
from typing import Any, Callable, Generic, Optional, TypeVar, cast
from uuid import UUID

from faker import Faker
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


def merge(*args: dict[str, Any]) -> dict[str, Any]:
    """helper function to shallow merge dictionaries"""
    output = {}
    for dictionary in args:
        for key, value in dictionary.items():
            output[key] = value
    return output


class ModelFactory(Generic[T]):
    def __init__(
        self, model: type[T], faker: Faker = Faker(), field_handlers: Optional[dict[str, Callable]] = None, **defaults
    ):
        self.faker = faker
        self.model = model
        self.defaults = defaults
        self.field_handlers = field_handlers

    def get_mock_value(self, field_type: Any) -> Any:
        if field_type is not None:
            faker_handler_map = {
                # primitives
                float: self.faker.pyfloat,
                int: self.faker.pyint,
                bool: self.faker.pybool,
                str: self.faker.pystr,
                # built-in objects
                dict: self.faker.pydict,
                tuple: self.faker.pydict,
                list: self.faker.pylist,
                set: self.faker.pyset,
                # standard library objects
                Decimal: self.faker.pydecimal,
                UUID: self.faker.uuid4,
                # datetime
                datetime: self.faker.date_time_between,
                date: self.faker.date_this_decade,
                time: self.faker.time,
            }
            handler = cast(Optional[Callable], faker_handler_map[field_type])
            if handler is not None:
                return handler()
        return None

    def build(self, **kwargs) -> T:
        parameters = merge(self.defaults, kwargs)
        for field_name, model_field in self.model.__fields__.items():
            if (
                parameters.get(field_name) is None
                and model_field.default is None
                and model_field.default_factory is None
            ):
                if self.field_handlers and field_name in self.field_handlers:
                    value = self.field_handlers[field_name]()
                else:
                    value = self.get_mock_value(field_type=model_field.type_)
                if value is not None:
                    parameters.setdefault(field_name, value)
        return self.model(**parameters)
