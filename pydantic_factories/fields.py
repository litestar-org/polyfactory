from typing import TYPE_CHECKING, Any, Callable

if TYPE_CHECKING:  # pragma: no cover
    from pydantic_factories.factory import ModelFactory


class FieldFactory:
    def __init__(self, builder_fn: Callable, **defaults):
        self.builder_fn = builder_fn
        self.defaults = defaults

    def to_value(self) -> Any:
        """Calls the field's builder_fn with the predefined defaults"""
        return self.builder_fn(**self.defaults)


class SubFactory(FieldFactory):
    def __init__(self, model_factory: "ModelFactory", **defaults):
        super().__init__(builder_fn=model_factory.build, **defaults)
