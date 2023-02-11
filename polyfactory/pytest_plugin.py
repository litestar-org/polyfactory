import re
from inspect import isclass
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    ClassVar,
    Dict,
    Literal,
    Optional,
    Type,
    Union,
)

from pytest import fixture

from polyfactory.exceptions import ParameterError

if TYPE_CHECKING:
    from pytest import Config  # nopycln: import

    from polyfactory.factories.base import BaseFactory


Scope = Union[
    Literal["session", "package", "module", "class", "function"],
    Callable[[str, "Config"], Literal["session", "package", "module", "class", "function"]],
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

    factory_class_map: ClassVar[Dict[Callable, Type["BaseFactory"]]] = {}

    def __init__(
        self,
        scope: "Scope" = "function",
        autouse: bool = False,
        name: Optional[str] = None,
    ):
        self.scope = scope
        self.autouse = autouse
        self.name = name

    def __call__(self, factory: Type["BaseFactory"]) -> Any:
        from polyfactory.factories.base import BaseFactory

        if not isclass(factory):
            raise ParameterError(f"{factory.__name__} is not a class.")

        if not issubclass(factory, BaseFactory):
            raise ParameterError(f"{factory.__name__} is not a BaseFactory subclass.")

        fixture_name = self.name or _get_fixture_name(factory.__name__)
        fixture_register = fixture(scope=self.scope, name=fixture_name, autouse=self.autouse)  # pyright: ignore

        def factory_fixture() -> Type["BaseFactory"]:
            return factory

        factory_fixture.__doc__ = factory.__doc__
        marker = fixture_register(factory_fixture)
        self.factory_class_map[marker] = factory
        return marker


def register_fixture(
    factory: Optional[Type["BaseFactory"]] = None,
    *,
    scope: "Scope" = "function",
    autouse: bool = False,
    name: Optional[str] = None,
) -> Any:
    """A decorator that allows registering model factories as fixtures.

    Args:
        factory: An optional factory class to decorate.
        scope: Pytest scope.
        autouse: Auto use fixture.
        name: Fixture name.

    Returns:
        A fixture factory instance.
    """
    factory_fixture = FactoryFixture(scope=scope, autouse=autouse, name=name)
    return factory_fixture(factory) if factory else factory_fixture
