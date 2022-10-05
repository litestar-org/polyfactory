import re
from dataclasses import dataclass
from typing import TYPE_CHECKING, Callable, Optional, Type, TypeVar, Union, overload

import pytest

if TYPE_CHECKING:
    from _pytest.config import Config
    from _pytest.scope import _ScopeName
    from pydantic import BaseModel

    from pydantic_factories import ModelFactory
    from pydantic_factories.protocols import DataclassProtocol

    Scope = Union["_ScopeName", Callable[[str, Config], "_ScopeName"]]
    T = TypeVar("T", bound=Union[BaseModel, DataclassProtocol])


def _get_fixture_name(name: str) -> str:
    """from inflection.underscore."""
    name = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", name)
    name = re.sub(r"([a-z\d])([A-Z])", r"\1_\2", name)
    name = name.replace("-", "_")
    return name.lower()


FixtureFunction = Callable[..., Type["ModelFactory"]]


@dataclass(frozen=True)
class PydanticFactoryFixtureMarker:
    scope: Scope
    autouse: bool = False
    name: Optional[str] = None

    def __call__(self, _class: Type["ModelFactory"]) -> FixtureFunction:
        fixture_name = self.name or _get_fixture_name(_class.__name__)
        fixture_registe = pytest.fixture(scope=self.scope, name=fixture_name, autouse=self.autouse)

        def factory_fixture() -> Type["ModelFactory"]:
            return _class

        factory_fixture.__doc__ = _class.__doc__
        return fixture_registe(factory_fixture)


@overload
def register_fixture(
    _class: None = ...,
    *,
    scope: Scope = ...,
    autouse: bool = ...,
    name: Optional[str] = ...,
) -> PydanticFactoryFixtureMarker:
    ...


@overload
def register_fixture(
    _class: Type["ModelFactory"] = ...,
    *,
    scope: Scope = ...,
    autouse: bool = ...,
    name: Optional[str] = ...,
) -> FixtureFunction:
    ...


def register_fixture(
    _class: Optional[Type["ModelFactory"]] = None,
    *,
    scope: Scope = "function",
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
