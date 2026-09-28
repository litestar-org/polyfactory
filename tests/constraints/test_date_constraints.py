from datetime import date, datetime, timedelta, timezone, tzinfo
from typing import Optional
from unittest.mock import patch

import pytest
from faker import Faker
from hypothesis import given
from hypothesis.strategies import dates, timezones

from pydantic import BaseModel, condate

from polyfactory.factories.pydantic_factory import ModelFactory
from polyfactory.value_generators.constrained_dates import handle_constrained_date


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
