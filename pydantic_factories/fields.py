from typing import Any, Callable


class Use:
    """
    A class used to wrap a callback function alongside args and kwargs.
    The callback will be invoked whenever building the given factory attribute.
    """

    def __init__(self, cb: Callable, *args: Any, **defaults: Any) -> None:
        self.cb = cb
        self.defaults = defaults
        self.args = args

    def to_value(self) -> Any:
        """invokes the callback function"""
        return self.cb(*self.args, **self.defaults)


class Require:
    """A placeholder class used to mark a given factory attribute as a required build-time kwarg"""


class Ignore:
    """A placeholder class used to mark a given factory attribute as ignored"""
