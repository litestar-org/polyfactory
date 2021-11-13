import os
from abc import ABC
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
from typing import Any, Callable, Dict, Generic, List, TypeVar
from uuid import UUID

from faker import Faker
from pydantic import BaseModel, ByteSize
from typing_extensions import Type

from pydantic_factories.exceptions import ConfigurationError

T = TypeVar("T", bound=BaseModel)

default_faker = Faker()


class ModelFactory(ABC, Generic[T]):
    __model__: Type[T]

    def __init__(self, faker: Faker = default_faker):
        self.faker = faker

        if not hasattr(self, "__model__"):
            raise ConfigurationError("missing model class in factory Meta")

    def get_mock_value(self, field_type: Any) -> Any:
        """
        Returns a mock value corresponding to the types supported by pydantic
        see: https://pydantic-docs.helpmanual.io/usage/types/
        """
        if field_type is not None:
            faker_handler_map: Dict[Any, Callable] = {
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

    def get_field_value(self, field_name: str, field_type: Any) -> Any:
        """Returns a field value on the sub-class if existing, otherwise returns a mock value"""
        try:
            return getattr(self, field_name)
        except AttributeError:
            return self.get_mock_value(field_type=field_type)

    def build(self, **kwargs) -> T:
        """builds an instance of the factory's Meta.model"""
        for field_name, model_field in self.__model__.__fields__.items():
            if kwargs.get(field_name) is None:
                kwargs.setdefault(field_name, self.get_field_value(field_name=field_name, field_type=model_field.type_))
        return self.__model__(**kwargs)

    def batch(self, size: int, **kwargs) -> List[T]:
        """builds a batch of size n of the factory's Meta.model"""
        return [self.build(**kwargs) for _ in range(size)]
