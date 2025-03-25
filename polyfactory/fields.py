from __future__ import annotations

from typing import Any, Callable, Generic, TypedDict, TypeVar, cast

from typing_extensions import ParamSpec

from polyfactory.exceptions import ParameterException
from polyfactory.utils import deprecation
from polyfactory.utils.predicates import is_safe_subclass

T = TypeVar("T")
P = ParamSpec("P")


class WrappedCallable(TypedDict):
    """A ref storing a callable. This class is a utility meant to prevent binding of methods."""

    value: Callable


class Require:
    """A factory field that marks an attribute as a required build-time kwarg."""


class NeverNone:
    """A factory field that marks as always generated, even if it's an optional"""


class Ignore:
    """A factory field that marks an attribute as ignored."""


class Use(Generic[P, T]):
    """Factory field used to wrap a callable.

    The callable will be invoked whenever building the given factory attribute.


    """

    __slots__ = ("args", "fn", "kwargs")

    def __init__(self, fn: Callable[P, T], *args: P.args, **kwargs: P.kwargs) -> None:
        """Wrap a callable.

        :param fn: A callable to wrap.
        :param args: Any args to pass to the callable.
        :param kwargs: Any kwargs to pass to the callable.
        """
        self.fn: WrappedCallable = {"value": fn}
        self.kwargs = kwargs
        self.args = args

    def to_value(self) -> T:
        """Invoke the callable.

        :returns: The output of the callable.


        """
        return cast("T", self.fn["value"](*self.args, **self.kwargs))


class PostGenerated:
    """Factory field that allows generating values after other fields are generated by the factory."""

    __slots__ = ("args", "fn", "kwargs")

    def __init__(self, fn: Callable, *args: Any, **kwargs: Any) -> None:
        """Designate field as post-generated.

        :param fn: A callable.
        :param args: Args for the callable.
        :param kwargs: Kwargs for the callable.
        """
        self.fn: WrappedCallable = {"value": fn}
        self.kwargs = kwargs
        self.args = args

    def to_value(self, name: str, values: dict[str, Any]) -> Any:
        """Invoke the post-generation callback passing to it the build results.

        :param name: Field name.
        :param values: Generated values.

        :returns: An arbitrary value.
        """
        return self.fn["value"](name, values, *self.args, **self.kwargs)


class Fixture:
    """Factory field to create a pytest fixture from a factory."""

    __slots__ = ("kwargs", "ref", "size")

    @deprecation.deprecated(version="2.20.0", alternative="Use factory directly")
    def __init__(self, fixture: Callable, size: int | None = None, **kwargs: Any) -> None:
        """Create a fixture from a factory.

        :param fixture: A factory that was registered as a fixture.
        :param size: Optional batch size.
        :param kwargs: Any build kwargs.
        """
        self.ref: WrappedCallable = {"value": fixture}
        self.size = size
        self.kwargs = kwargs

    def to_value(self) -> Any:
        """Call the factory's build or batch method.

        :raises: ParameterException

        :returns: The build result.
        """
        from polyfactory.factories.base import BaseFactory

        factory = self.ref["value"]
        if not is_safe_subclass(factory, BaseFactory):
            msg = "fixture has not been registered using the register_factory decorator"
            raise ParameterException(msg)

        if self.size is not None:
            return factory.batch(self.size, **self.kwargs)
        return factory.build(**self.kwargs)
