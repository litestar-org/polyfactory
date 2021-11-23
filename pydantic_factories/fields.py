from typing import TYPE_CHECKING, Any, Callable

if TYPE_CHECKING:  # pragma: no cover
    from pydantic_factories.factory import ModelFactory


class Use:
    def __init__(self, cb: Callable, *args, **defaults):
        self.cb = cb
        self.defaults = defaults
        self.args = args

    def to_value(self) -> Any:
        """Calls the field's cb with the predefined defaults"""
        return self.cb(*self.args, **self.defaults)


class SubFactory(Use):
    def __init__(self, model_factory: "ModelFactory", **defaults):
        super().__init__(cb=model_factory.build, **defaults)
