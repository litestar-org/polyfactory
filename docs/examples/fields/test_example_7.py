from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict

from polyfactory import PostGenerated
from polyfactory.factories import DataclassFactory


def add_timedelta(name: str, values: Dict[str, datetime], *args: Any, **kwargs: Any) -> datetime:
    delta = timedelta(days=1)
    return values["from_dt"] + delta


@dataclass
class DatetimeRange:
    to_dt: datetime
    from_dt: datetime = field(default_factory=datetime.now)


class DatetimeRangeFactory(DataclassFactory[DatetimeRange]):
    to_dt = PostGenerated(add_timedelta)


def test_post_generated() -> None:
    date_range_instance = DatetimeRangeFactory.build()
    assert date_range_instance.to_dt == date_range_instance.from_dt + timedelta(days=1)
