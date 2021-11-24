from typing import TYPE_CHECKING, Any, Callable

if TYPE_CHECKING:  # pragma: no cover
    from pydantic_factories.factory import ModelFactory


class Use:
    """
    A class used to wrap a callback function alongside args and kwargs.
    The callback will be invoked whenever building the given factory attribute.
    """

    def __init__(self, cb: Callable, *args, **defaults):
        self.cb = cb
        self.defaults = defaults
        self.args = args

    def to_value(self) -> Any:
        """Calls the field's cb with the predefined defaults"""
        return self.cb(*self.args, **self.defaults)


class SubFactory(Use):
    """A class used to wrap an instance of ModelFactory alongside defaults to be used"""

    def __init__(self, model_factory: "ModelFactory", **defaults):
        super().__init__(cb=model_factory.build, **defaults)


class BuildKwarg:
    """A placeholder class used to mark a given factory attribute as a required build-time kwarg"""


class Ignored:
    """A placeholder class used to mark a given factory attribute as ignored"""
