import os
from base64 import b64encode
from collections import deque
from datetime import date, datetime, time, timedelta
from decimal import Decimal
from ipaddress import (
    IPv4Address,
    IPv4Interface,
    IPv4Network,
    IPv6Address,
    IPv6Interface,
    IPv6Network,
)
from pathlib import Path
from typing import Any, Callable, Generic, Optional, TypeVar
from uuid import UUID

from faker import Faker
from pydantic import BaseModel, ByteSize

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
        self, model: type[T], faker: Optional[Faker], field_handlers: Optional[dict[str, Callable]] = None, **defaults
    ):
        self.model = model
        self.defaults = defaults
        self.field_handlers = field_handlers
        if faker:
            self.faker = faker
        else:
            self.faker = Faker()

    def get_mock_value(self, field_type: Any) -> Any:
        """
        Returns a mock value corresponding to the types supported by pydantic
        see: https://pydantic-docs.helpmanual.io/usage/types/
        """
        if field_type is not None:
            faker_handler_map: dict[Any, Callable] = {
                # primitives
                float: self.faker.pyfloat,
                int: self.faker.pyint,
                bool: self.faker.pybool,
                str: self.faker.pystr,
                bytes: lambda: b64encode(self.faker.pystr().encode("utf-8")).decode("utf-8"),
                # built-in objects
                dict: self.faker.pydict,
                tuple: self.faker.pydict,
                list: self.faker.pylist,
                set: self.faker.pyset,
                frozenset: self.faker.pylist,
                deque: self.faker.pylist,
                # standard library objects
                Path: lambda: Path(os.path.realpath(__file__)),
                Decimal: self.faker.pydecimal,
                UUID: self.faker.uuid4,
                # datetime
                datetime: self.faker.date_time_between,
                date: self.faker.date_this_decade,
                time: self.faker.time,
                timedelta: self.faker.time_delta,
                # ip addresses
                IPv4Address: self.faker.ipv4,
                IPv4Interface: self.faker.ipv4,
                IPv4Network: lambda: self.faker.ipv4(network=True),
                IPv6Address: self.faker.ipv6,
                IPv6Interface: self.faker.ipv6,
                IPv6Network: lambda: self.faker.ipv6(network=True),
                # pydantic specific
                ByteSize: lambda: b64encode(self.faker.pystr().encode("utf-8")).decode("utf-8"),
            }
            handler = faker_handler_map[field_type]
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
