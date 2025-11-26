"""Test datetime constraints, including Issue #734."""

import contextlib
from datetime import datetime, timedelta, timezone
from typing import Annotated, Optional

import pytest
from annotated_types import Timezone
from hypothesis import given
from hypothesis.strategies import datetimes

from pydantic import BaseModel, Field, __version__

with contextlib.suppress(ImportError):
    from pydantic import BeforeValidator


from polyfactory.factories.pydantic_factory import ModelFactory


@given(
    datetimes(min_value=datetime(1900, 1, 1), max_value=datetime.now() - timedelta(days=3)),
    datetimes(min_value=datetime.now(), max_value=datetime(2100, 1, 1)),
)
@pytest.mark.parametrize(
    ("start", "end"),
    (
        ("ge", "le"),
        ("gt", "lt"),
        ("ge", "lt"),
        ("gt", "le"),
    ),
)
def test_handle_constrained_datetime(
    start: Optional[str],
    end: Optional[str],
    start_datetime: datetime,
    end_datetime: datetime,
) -> None:
    """Test that constrained datetimes are generated correctly."""
    if start_datetime == end_datetime:
        return

    kwargs: dict[str, datetime] = {}
    if start:
        kwargs[start] = start_datetime
    if end:
        kwargs[end] = end_datetime

    class MyModel(BaseModel):
        value: datetime = Field(**kwargs)  # type: ignore

    class MyFactory(ModelFactory[MyModel]): ...

    result = MyFactory.build()

    assert result.value
    assert isinstance(result.value, datetime), "Should be datetime.datetime, not date"
    assert result.value >= start_datetime
    assert result.value <= end_datetime


@pytest.mark.skipif(__version__.startswith("1"), reason="Pydantic v2 required")
def test_annotated_datetime_with_validator_and_constraint() -> None:
    def validate_datetime(value: datetime) -> datetime:
        """Validator that expects a datetime object with timezone info."""
        assert isinstance(value, datetime), f"Expected datetime.datetime, got {type(value)}"
        assert value.tzinfo == timezone.utc, f"Expected UTC timezone, got {value.tzinfo}"
        return value

    ValidatedDatetime = Annotated[datetime, BeforeValidator(validate_datetime), Timezone(tz=timezone.utc)]
    minimum_datetime = datetime(2030, 1, 1, tzinfo=timezone.utc)

    class MyModel(BaseModel):
        dt: ValidatedDatetime = Field(gt=minimum_datetime)  # pyright: ignore[reportInvalidTypeForm]

    class MyModelFactory(ModelFactory[MyModel]): ...

    instance = MyModelFactory.build()
    assert isinstance(instance.dt, datetime), "Should be datetime.datetime"
    assert instance.dt.tzinfo == timezone.utc, "Should have UTC timezone"
    assert instance.dt > minimum_datetime, "Should respect gt constraint"
