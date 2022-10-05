import inspect
import re
from dataclasses import dataclass
from typing import TYPE_CHECKING, Callable, Optional, Type, Union, overload

import pytest

from pydantic_factories.factory import ModelFactory

if TYPE_CHECKING:
    from _pytest.config import Config
    from _pytest.scope import _ScopeName

    Scope = Union["_ScopeName", Callable[[str, Config], "_ScopeName"]]


split_pattern_1 = re.compile(r"([A-Z]+)([A-Z][a-z])")
split_pattern_2 = re.compile(r"([a-z\d])([A-Z])")


def _get_fixture_name(name: str) -> str:
    """from inflection.underscore."""
    name = re.sub(split_pattern_1, r"\1_\2", name)
    name = re.sub(split_pattern_2, r"\1_\2", name)
    name = name.replace("-", "_")
    return name.lower()


FixtureFunction = Callable[..., Type["ModelFactory"]]


@dataclass(frozen=True)
class PydanticFactoryFixtureMarker:
    scope: "Scope"
    autouse: bool = False
    name: Optional[str] = None

    def __call__(self, _class: Type["ModelFactory"]) -> FixtureFunction:
        if not inspect.isclass(_class):
            raise ValueError(f"{_class.__name__} is not a class.")
        if not issubclass(_class, ModelFactory):
            raise ValueError(f"{_class.__name__} is not a ModelFactory class.")

        fixture_name = self.name or _get_fixture_name(_class.__name__)
        fixture_registe = pytest.fixture(scope=self.scope, name=fixture_name, autouse=self.autouse)

        def factory_fixture() -> Type["ModelFactory"]:
            return _class

        factory_fixture.__doc__ = _class.__doc__
        return fixture_registe(factory_fixture)


@overload
def register_fixture(
    _class: None = None,
    *,
    scope: "Scope" = ...,
    autouse: bool = ...,
    name: Optional[str] = ...,
) -> PydanticFactoryFixtureMarker:
    ...


@overload
def register_fixture(
    _class: Type["ModelFactory"],
    *,
    scope: "Scope" = ...,
    autouse: bool = ...,
    name: Optional[str] = ...,
) -> FixtureFunction:
    ...


def register_fixture(
    _class: Optional[Type["ModelFactory"]] = None,
    *,
    scope: "Scope" = "function",
    autouse: bool = False,
    name: Optional[str] = None,
) -> Union[PydanticFactoryFixtureMarker, FixtureFunction]:
    """A decorator to wrap a ModelFactory as a pytest fixture.

    Accept pytest.fixture-like keyword arguments, including `scope`,
    `autouse`, `name`.
    """

    fixture_marker = PydanticFactoryFixtureMarker(scope=scope, autouse=autouse, name=name)

    if _class:
        return fixture_marker(_class)

    return fixture_marker
