from copy import copy
from typing import Any, Callable, Dict, Generic, Optional, TypeVar, cast

from typing_extensions import ParamSpec, TypedDict

from polyfactory.exceptions import ParameterError
from polyfactory.pytest_plugin import FactoryFixture

T = TypeVar("T")
P = ParamSpec("P")


class WrappedCallable(TypedDict):
    value: Callable


class Use(Generic[P, T]):
    __slots__ = ("fn", "kwargs", "args")

    def __init__(self, fn: Callable[P, T], *args: P.args, **kwargs: P.kwargs) -> None:
        """A class used to wrap a callable alongside any args and kwargs.

        The callable will be invoked whenever building the given factory
        attribute.

        Args:
            fn: A callable.
            *args: Args for the callable.
            **kwargs: Kwargs for the callable.
        """
        self.fn: WrappedCallable = {"value": fn}
        self.kwargs = kwargs
        self.args = args

    def to_value(self) -> T:
        """Invokes the callable.

        Returns:
            The output of the callable.
        """
        return cast("T", self.fn["value"](*self.args, **self.kwargs))


class PostGenerated:
    __slots__ = ("fn", "kwargs", "args")

    def __init__(self, fn: Callable, *args: Any, **kwargs: Any) -> None:
        """A class that allows for generating values after other fields are generated.

        Args:
            fn: A callable.
            *args: Args for the callable.
            **kwargs: Kwargs for the callable.
        """
        self.fn: WrappedCallable = {"value": fn}
        self.kwargs = kwargs
        self.args = args

    def to_value(self, name: str, values: Dict[str, Any]) -> Any:
        """Invokes the post generation callback.

        Args:
            name: Field name.
            values: Generated values.

        Returns:
            An arbitrary value.
        """
        return self.fn["value"](name, values, *self.args, **self.kwargs)


class Require:
    """A placeholder class used to mark a given factory attribute as a required build-time kwarg."""


class Ignore:
    """A placeholder class used to mark a given factory attribute as ignored."""


class Fixture:
    __slots__ = ("fixture", "size", "kwargs")

    def __init__(self, fixture: Callable, size: Optional[int] = None, **kwargs: Any) -> None:
        """A class that allows using ModelFactory classes registered as pytest fixtures as factory fields.

        Args:
            fixture: A factory that was registered as a fixture.
            size: Optional batch size.
            **kwargs: Any build kwargs.
        """
        self.fixture: WrappedCallable = {"value": fixture}
        self.size = size
        self.kwargs = kwargs

    def to_value(self, **kwargs: Any) -> Any:
        """
        Retries the correct factory for the fixture, calling either its build method - or if size is given, batch.

        Returns:
            The build result.
        """

        if factory := FactoryFixture.factory_class_map.get(self.fixture["value"]):
            kwds = copy(self.kwargs)
            kwds.update(kwargs)

            if self.size:
                return factory.batch(self.size, **kwds)
            return factory.build(**kwds)
        raise ParameterError("fixture has not been registered using the register_factory decorator")
