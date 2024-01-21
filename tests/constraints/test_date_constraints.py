from datetime import date, timedelta
from typing import Dict, Optional

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
        kwargs: Dict[str, date] = {}
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
