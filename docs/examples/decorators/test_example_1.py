from dataclasses import dataclass, field
from datetime import datetime, timedelta

from polyfactory.decorators import post_generated
from polyfactory.factories import DataclassFactory


@dataclass
class DatetimeRange:
    to_dt: datetime
    from_dt: datetime = field(default_factory=datetime.now)


class DatetimeRangeFactory(DataclassFactory[DatetimeRange]):
    @post_generated
    @classmethod
    def to_dt(cls, from_dt: datetime) -> datetime:
        return from_dt + cls.__faker__.time_delta("+3d")


def test_post_generated() -> None:
    date_range_instance = DatetimeRangeFactory.build()
    assert date_range_instance.to_dt > date_range_instance.from_dt
    assert date_range_instance.to_dt < date_range_instance.from_dt + timedelta(days=3)
