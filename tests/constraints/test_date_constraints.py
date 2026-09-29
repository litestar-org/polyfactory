from datetime import date, datetime, timedelta, timezone, tzinfo
from typing import Annotated, Optional
from unittest.mock import patch

import msgspec
import pytest
from faker import Faker
from hypothesis import given
from hypothesis.strategies import dates, timezones

from pydantic import BaseModel, Field, condate

from polyfactory.factories.msgspec_factory import MsgspecFactory
from polyfactory.factories.pydantic_factory import ModelFactory
from polyfactory.value_generators.constrained_dates import handle_constrained_date, handle_constrained_datetime


@given(
    dates(max_value=date.today() - timedelta(days=3)),
    dates(min_value=date.today()),
)
@pytest.mark.parametrize(("start", "end"), (("ge", "le"), ("gt", "lt"), ("ge", "lt"), ("gt", "le")))
def test_handle_constrained_date(
    start: Optional[str],
    end: Optional[str],
    start_date: date,
    end_date: date,
) -> None:
    if start_date != end_date:
        kwargs: dict[str, date] = {}
        if start:
            kwargs[start] = start_date
        if end:
            kwargs[end] = end_date

        class MyModel(BaseModel):
            value: condate(**kwargs)  # type: ignore

        class MyFactory(ModelFactory):
            __model__ = MyModel

        result = MyFactory.build()

        assert result.value


@given(tz=timezones())
def test_handle_constrained_date_tz(tz: tzinfo) -> None:
    faker = Faker()

    # Create a fixed UTC time close to midnight (23:00) so that positive timezone offsets shift the date to tomorrow.
    fixed_utc_now = datetime(2020, 1, 1, 23, 0, 0, tzinfo=timezone.utc)

    def mock_now(tz: Optional[tzinfo] = None) -> datetime:
        if tz is not None:
            return fixed_utc_now.astimezone(tz)
        return fixed_utc_now

    with patch("polyfactory.value_generators.constrained_dates.datetime") as mock_datetime:
        mock_datetime.now.side_effect = mock_now

        expected_start = fixed_utc_now.astimezone(tz).date() - timedelta(days=100)
        expected_end = fixed_utc_now.astimezone(tz).date() + timedelta(days=100)

        # Test 1: By setting 'ge' to the expected end_date, we force start_date == end_date.
        # This proves the tz parameter was used to calculate end_date properly.
        # If the tz bug existed, Faker would raise a ValueError because expected_end (ge) would be > end_date.
        assert handle_constrained_date(faker=faker, tz=tz, ge=expected_end) == expected_end

        # Test 2: Do the same for the start_date logic using 'le'.
        assert handle_constrained_date(faker=faker, tz=tz, le=expected_start) == expected_start


@pytest.mark.parametrize(("start", "end"), (("ge", "le"), ("gt", "lt"), ("ge", "lt"), ("gt", "le")))
@pytest.mark.parametrize("tz", (None, timezone.utc, timezone(timedelta(hours=5))))
def test_handle_constrained_datetime(start: str, end: str, tz: Optional[tzinfo]) -> None:
    start_datetime = datetime(2022, 1, 1, tzinfo=tz)
    end_datetime = datetime(2022, 1, 2, tzinfo=tz)

    kwargs: dict[str, datetime] = {start: start_datetime, end: end_datetime}
    result = handle_constrained_datetime(faker=Faker(), **kwargs)  # type: ignore[arg-type]

    assert isinstance(result, datetime)
    assert result.tzinfo == tz
    assert (start_datetime <= result) if start == "ge" else (start_datetime < result)
    assert (result <= end_datetime) if end == "le" else (result < end_datetime)


@pytest.mark.parametrize(("tz", "expected_tz"), ((True, timezone.utc), (False, None), (None, None)))
def test_handle_constrained_datetime_tz(tz: Optional[bool], expected_tz: Optional[tzinfo]) -> None:
    result = handle_constrained_datetime(faker=Faker(), tz=tz)

    assert isinstance(result, datetime)
    assert result.tzinfo == expected_tz


@pytest.mark.parametrize("constraint", ("ge", "gt", "le", "lt"))
def test_handle_constrained_datetime_single_bound(constraint: str) -> None:
    bound = datetime.now(tz=timezone.utc) + timedelta(days=365)

    result = handle_constrained_datetime(faker=Faker(), **{constraint: bound})  # type: ignore[arg-type]

    assert isinstance(result, datetime)
    assert result.tzinfo == timezone.utc
    if constraint in ("ge", "gt"):
        assert result > bound if constraint == "gt" else result >= bound
    else:
        assert result < bound if constraint == "lt" else result <= bound


def test_constrained_datetime_pydantic_field() -> None:
    lower = datetime(2022, 1, 1, tzinfo=timezone.utc)

    class MyModel(BaseModel):
        value: Annotated[datetime, Field(gt=lower)]

    class MyFactory(ModelFactory):
        __model__ = MyModel

    for _ in range(10):
        result = MyFactory.build()

        assert isinstance(result.value, datetime)
        assert result.value.tzinfo is not None
        assert result.value > lower


def test_constrained_datetime_msgspec_tz() -> None:
    class MyStruct(msgspec.Struct):
        aware: Annotated[datetime, msgspec.Meta(tz=True)]
        naive: Annotated[datetime, msgspec.Meta(tz=False)]

    class MyFactory(MsgspecFactory[MyStruct]):
        __model__ = MyStruct

    result = MyFactory.build()

    assert isinstance(result.aware, datetime)
    assert result.aware.tzinfo is not None
    assert isinstance(result.naive, datetime)
    assert result.naive.tzinfo is None
