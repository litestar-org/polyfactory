from typing import Any, Callable, Dict, TypeVar

from typing_extensions import ParamSpec

T = TypeVar("T")
P = ParamSpec("P")


class Use:
    """A class used to wrap a callback function alongside args and kwargs.

    The callback will be invoked whenever building the given factory
    attribute.
    """

    def __init__(self, cb: Callable[P, T], *args: P.args, **kwargs: P.kwargs) -> None:
        self.cb = cb
        self.kwargs = kwargs
        self.args = args

    def to_value(self) -> Any:
        """invokes the callback function."""
        return self.cb(*self.args, **self.kwargs)


class PostGenerated:
    """A class to allow post generating using already generated values. The
    callback will be invoked after building all non post generated factory
    attributes.

    Callback should be able to receive the field name as its first
    argument and a dictionary of values as its second argument.
    """

    def __init__(self, cb: Callable, *args: Any, **kwargs: Any) -> None:
        self.cb = cb
        self.kwargs = kwargs
        self.args = args

    def to_value(self, name: str, values: Dict[str, Any]) -> Any:
        """invokes the callback function."""
        return self.cb(name, values, *self.args, **self.kwargs)


class Require:
    """A placeholder class used to mark a given factory attribute as a required
    build-time kwarg."""


class Ignore:
    """A placeholder class used to mark a given factory attribute as
    ignored."""
