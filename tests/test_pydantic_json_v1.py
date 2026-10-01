"""Pydantic v1 JSON fields, including v1's compatibility API under v2."""

import json
import sys
from datetime import date
from importlib import import_module
from types import GenericAlias
from typing import Any, Optional, get_origin

import pytest

import pydantic

from polyfactory.factories.pydantic_factory import ModelFactory

if sys.version_info >= (3, 14):
    pytest.skip("pydantic v1 not supported on Python 3.14", allow_module_level=True)

pydantic_v1 = import_module("pydantic" if pydantic.VERSION.startswith("1") else "pydantic.v1")


@pytest.mark.parametrize("optional", [False, True])
@pytest.mark.parametrize("inner_type", [int, date, list[int], dict[str, str], pydantic_v1.BaseModel])
def test_json_fields(inner_type: Any, optional: bool) -> None:
    if inner_type is pydantic_v1.BaseModel:
        inner_type = pydantic_v1.create_model("JsonContent", value=(int, ...))
    annotation: Any = pydantic_v1.Json[inner_type]
    if optional:
        annotation = Optional[annotation]
    model = pydantic_v1.create_model("JsonModel", value=(annotation, ...))
    factory = ModelFactory.create_factory(model, __allow_none_optionals__=False)
    factory.seed_random(0)

    for _ in range(3):
        instance = factory.build()
        assert isinstance(instance.value, get_origin(inner_type) or inner_type)
        constructed = factory.build(factory_use_construct=True)
        assert isinstance(constructed.value, (str, bytes, bytearray))
        model(value=constructed.value)
        json.loads(constructed.value)


def test_unparameterized_json_field() -> None:
    model = pydantic_v1.create_model("AnyJsonModel", value=(pydantic_v1.Json, ...))
    factory = ModelFactory.create_factory(model)
    for _ in range(3):
        factory.build()


def test_json_inner_constraints_and_coverage() -> None:
    constrained = pydantic_v1.conint(ge=100, le=200)
    model = pydantic_v1.create_model(
        "ConstrainedJsonModel", value=(pydantic_v1.Json[GenericAlias(list, constrained)], ...)
    )
    factory = ModelFactory.create_factory(model)
    for instance in [*factory.batch(3), *factory.coverage()]:
        assert instance.value
        assert all(100 <= value <= 200 for value in instance.value)


def test_optional_json_none_and_field_metadata() -> None:
    model = pydantic_v1.create_model("OptionalJsonModel", value=(Optional[pydantic_v1.Json[int]], None))
    field = model.__fields__["value"]
    original_annotation = field.annotation
    original_outer_type = field.outer_type_
    factory = ModelFactory.create_factory(model)
    factory.seed_random(0)
    values = [instance.value for instance in factory.batch(20)]
    assert None in values
    assert any(isinstance(value, int) for value in values)
    assert field.annotation is original_annotation
    assert field.outer_type_ is original_outer_type
    assert field.parse_json is True


def test_json_fields_inside_collection() -> None:
    annotation = GenericAlias(list, pydantic_v1.Json[dict[str, int]])
    model = pydantic_v1.create_model("NestedJsonModel", value=(annotation, ...))
    factory = ModelFactory.create_factory(model)
    for instance in factory.batch(3):
        assert instance.value
        assert all(isinstance(value, dict) for value in instance.value)
