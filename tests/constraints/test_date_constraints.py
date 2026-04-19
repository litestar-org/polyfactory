from datetime import date, timedelta, timezone
from typing import Optional
from unittest.mock import patch, MagicMock

import pytest
from hypothesis import given
from hypothesis.strategies import dates

from pydantic import BaseModel, condate

from polyfactory.factories.pydantic_factory import ModelFactory


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

def test_handle_constrained_date_tz() -> None:
    from polyfactory.value_generators.constrained_dates import handle_constrained_date
    from faker import Faker
    
    faker = Faker()
    tz = timezone(timedelta(hours=5))
    
    with patch("polyfactory.value_generators.constrained_dates.datetime") as mock_datetime:
        mock_now = MagicMock()
        mock_now.date.return_value = date(2020, 1, 1)
        mock_datetime.now.return_value = mock_now
        
        handle_constrained_date(faker=faker, tz=tz)
        
        assert mock_datetime.now.call_count == 2
        for call in mock_datetime.now.call_args_list:
            assert call.kwargs.get("tz") == tz
