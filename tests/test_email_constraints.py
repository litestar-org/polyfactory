from random import Random
from typing import Annotated, Optional

import pytest
from email_validator import validate_email

import pydantic
from pydantic import EmailStr, Field

from polyfactory.exceptions import ParameterException
from polyfactory.factories.base import BaseFactory
from polyfactory.factories.pydantic_factory import _IS_PYDANTIC_V1, ModelFactory
from polyfactory.field_meta import FieldMeta
from polyfactory.value_generators.constrained_email import handle_constrained_email

IS_PYDANTIC_V1 = _IS_PYDANTIC_V1


@pytest.mark.skipif(IS_PYDANTIC_V1, reason="EmailStr Field constraints require Pydantic v2")
@pytest.mark.parametrize("bounds", [{"max_length": 20}, {"min_length": 5, "max_length": 50}])
def test_email_string_length_constraints(bounds: dict[str, int]) -> None:
    model = pydantic.create_model(
        "ConstrainedEmailModel",
        email=(EmailStr, Field(min_length=bounds.get("min_length"), max_length=bounds.get("max_length"))),
    )
    factory: type[BaseFactory] = ModelFactory.create_factory(model)
    for instance in [factory.build(), *factory.coverage()]:
        assert isinstance(instance.email, str)
        assert bounds.get("min_length", 0) <= len(instance.email) <= bounds["max_length"]


@pytest.mark.parametrize("length", [5, 6, 7, 20, 64, 68, 69, 127, 128, 129, 130, 131, 132, 133, 134, 190, 254])
def test_constrained_email_exact_lengths(length: int) -> None:
    value = handle_constrained_email(Random(length), min_length=length, max_length=length)
    assert len(value) == length
    assert validate_email(value, check_deliverability=False).normalized == value
    local, domain = value.split("@")
    assert len(local) <= 64
    assert all(0 < len(label) <= 63 for label in domain.split("."))


@pytest.mark.parametrize("bounds", [{}, {"min_length": 100}, {"max_length": 20}, {"min_length": 0, "max_length": 1000}])
def test_constrained_email_open_bounds_and_seed(bounds: dict[str, int]) -> None:
    random = Random(42)
    values = [handle_constrained_email(random, **bounds) for _ in range(20)]
    repeated = Random(42)
    assert values == [handle_constrained_email(repeated, **bounds) for _ in range(20)]
    assert len(set(values)) > 1
    for value in values:
        assert max(5, bounds.get("min_length", 5)) <= len(value) <= min(254, bounds.get("max_length", 254))
        assert validate_email(value, check_deliverability=False).normalized == value


@pytest.mark.parametrize(
    "bounds",
    [
        {"min_length": -1},
        {"max_length": -1},
        {"min_length": 20, "max_length": 10},
        {"max_length": 0},
        {"max_length": 4},
        {"min_length": 255},
    ],
)
def test_constrained_email_impossible_lengths(bounds: dict[str, int]) -> None:
    with pytest.raises(ParameterException):
        handle_constrained_email(Random(0), **bounds)


@pytest.mark.skipif(IS_PYDANTIC_V1, reason="EmailStr Field constraints require Pydantic v2")
def test_email_string_nested_optional_and_annotated_lengths() -> None:
    constrained = Annotated[EmailStr, Field(min_length=20, max_length=20)]
    inner = pydantic.create_model("EmailInner", email=(constrained, ...))
    model = pydantic.create_model(
        "EmailContainer",
        optional=(Optional[constrained], ...),
        items=(list[constrained], ...),
        mapping=(dict[constrained, constrained], ...),
        nested=(inner, ...),
        ordinary=(str, Field(min_length=3, max_length=3)),
    )
    factory: type[BaseFactory] = ModelFactory.create_factory(model, __allow_none_optionals__=False)
    built = factory.build()
    covered = list(factory.coverage())
    assert built.optional is not None
    assert {instance.optional is None for instance in covered} == {True, False}
    for instance in [built, *covered]:
        if instance.optional is not None:
            assert isinstance(instance.optional, str) and len(instance.optional) == 20
        values = [
            *instance.items,
            *instance.mapping,
            *instance.mapping.values(),
            instance.nested.email,
        ]
        assert all(isinstance(value, str) and len(value) == 20 for value in values)
        assert len(instance.ordinary) == 3


@pytest.mark.skipif(IS_PYDANTIC_V1, reason="EmailStr Field constraints require Pydantic v2")
@pytest.mark.parametrize("bounds", [{"max_length": 4}, {"min_length": 255}])
def test_email_string_impossible_model_lengths(bounds: dict[str, int]) -> None:
    model = pydantic.create_model(
        "ImpossibleEmail",
        email=(EmailStr, Field(min_length=bounds.get("min_length"), max_length=bounds.get("max_length"))),
    )
    factory: type[BaseFactory] = ModelFactory.create_factory(model)
    with pytest.raises(ParameterException, match="email length constraints"):
        factory.build()
    with pytest.raises(ParameterException, match="Unsupported type") as exc:
        list(factory.coverage())
    assert isinstance(exc.value.__cause__, ParameterException)
    assert "email length constraints" in str(exc.value.__cause__)


def test_email_string_unconstrained_provider_unchanged() -> None:
    model = pydantic.create_model("UnconstrainedEmail", email=(EmailStr, ...))
    factory: type[BaseFactory] = ModelFactory.create_factory(model)
    factory.__faker__.seed_instance(42)
    expected = factory.__faker__.free_email()
    factory.__faker__.seed_instance(42)
    assert factory.build().email == expected
    factory.__faker__.seed_instance(42)
    assert next(factory.coverage()).email == expected


@pytest.mark.skipif(IS_PYDANTIC_V1, reason="EmailStr Field constraints require Pydantic v2")
def test_email_string_other_constraints_remain_unsupported() -> None:
    meta = FieldMeta.from_type(annotation=EmailStr, name="email", constraints={"pattern": "example"})
    with pytest.raises(ParameterException, match="received constraints for unsupported type"):
        ModelFactory.get_constrained_field_value(EmailStr, meta)
