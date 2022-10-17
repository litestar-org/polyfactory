import re
from inspect import isclass
from typing import Any, Callable, ClassVar, Dict, Optional, Type, Union

import pytest
from _pytest.config import Config
from pydantic import validate_arguments
from typing_extensions import Literal

from pydantic_factories.exceptions import ParameterError
from pydantic_factories.factory import ModelFactory

Scope = Union[
    Literal["session", "package", "module", "class", "function"],
    Callable[[str, Config], Literal["session", "package", "module", "class", "function"]],
]


split_pattern_1 = re.compile(r"([A-Z]+)([A-Z][a-z])")
split_pattern_2 = re.compile(r"([a-z\d])([A-Z])")


def _get_fixture_name(name: str) -> str:
    """from inflection.underscore."""
    name = re.sub(split_pattern_1, r"\1_\2", name)
    name = re.sub(split_pattern_2, r"\1_\2", name)
    name = name.replace("-", "_")
    return name.lower()


class FactoryFixture:
    __slots__ = ("scope", "autouse", "name")

    factory_class_map: ClassVar[Dict[Callable, Type["ModelFactory"]]] = {}

    @validate_arguments
    def __init__(
        self,
        scope: "Scope" = "function",
        autouse: bool = False,
        name: Optional[str] = None,
    ):
        self.scope = scope
        self.autouse = autouse
        self.name = name

    def __call__(self, model_factory: Type["ModelFactory"]) -> Any:
        if not isclass(model_factory):
            raise ParameterError(f"{model_factory.__name__} is not a class.")
        if not issubclass(model_factory, ModelFactory):
            raise ParameterError(f"{model_factory.__name__} is not a ModelFactory subclass.")

        fixture_name = self.name or _get_fixture_name(model_factory.__name__)
        fixture_register = pytest.fixture(scope=self.scope, name=fixture_name, autouse=self.autouse)  # pyright: ignore

        def factory_fixture() -> Type["ModelFactory"]:
            return model_factory

        factory_fixture.__doc__ = model_factory.__doc__
        marker = fixture_register(factory_fixture)
        self.factory_class_map[marker] = model_factory
        return marker


def register_fixture(
    model_factory: Optional[Type["ModelFactory"]] = None,
    *,
    scope: "Scope" = "function",
    autouse: bool = False,
    name: Optional[str] = None,
) -> Any:
    """A decorator that allows registering model factories as fixtures.

    Args:
        model_factory: An optional model factory class to decorate.
        scope: Pytest scope.
        autouse: Auto use fixture.
        name: Fixture name.

    Returns:
        A fixture factory instance.
    """
    fixture = FactoryFixture(scope=scope, autouse=autouse, name=name)
    return fixture(model_factory) if model_factory else fixture
