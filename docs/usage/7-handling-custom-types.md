# Handling Custom Types

If your model has an attribute that is not supported by `polyfactory` and
it depends on third party libraries, you can create your custom extension
subclassing the `ModelFactory`, and overriding the `get_mock_value` method to
add your logic.

```python
from typing import Any
from polyfactory.factories.pydantic_factory import ModelFactory


class CustomFactory(ModelFactory[Any]):
    """Tweak the ModelFactory to add our custom mocks."""

    @classmethod
    def get_mock_value(cls, field_type: Any) -> Any:
        """Add our custom mock value."""
        if str(field_type) == "my_super_rare_datetime_field":
            return cls.get_faker().date_time_between()

        return super().get_mock_value(field_type)
```

Where `cls.get_faker()` is a `faker` instance that you can use to build your
returned value.
