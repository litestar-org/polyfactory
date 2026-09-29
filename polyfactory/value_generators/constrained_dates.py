from __future__ import annotations

from datetime import date, datetime, timedelta, timezone, tzinfo
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from faker import Faker


def handle_constrained_date(
    faker: Faker,
    ge: date | None = None,
    gt: date | None = None,
    le: date | None = None,
    lt: date | None = None,
    tz: tzinfo | bool | None = timezone.utc,
) -> date:
    """Generates a date value fulfilling the expected constraints.

    :param faker: An instance of faker.
    :param lt: Less than value.
    :param le: Less than or equal value.
    :param gt: Greater than value.
    :param ge: Greater than or equal value.
    :param tz: A timezone. When a boolean is passed (as used by ``msgspec.Meta``),
        ``True`` maps to ``timezone.utc`` (timezone-aware) and ``False`` maps to
        ``None`` (timezone-naive), matching the semantics of ``msgspec.Meta(tz=...)``.

    :returns: A date instance.
    """
    if isinstance(tz, bool):
        tz = timezone.utc if tz else None

    start_date = datetime.now(tz=tz).date() - timedelta(days=100)
    if ge:
        start_date = ge
    elif gt:
        start_date = gt + timedelta(days=1)

    end_date = datetime.now(tz=tz).date() + timedelta(days=100)
    if le:
        end_date = le
    elif lt:
        end_date = lt - timedelta(days=1)

    return faker.date_between(start_date=start_date, end_date=end_date)


def handle_constrained_datetime(
    faker: Faker,
    ge: datetime | None = None,
    gt: datetime | None = None,
    le: datetime | None = None,
    lt: datetime | None = None,
    tz: tzinfo | bool | None = timezone.utc,
) -> datetime:
    """Generates a datetime value fulfilling the expected constraints.

    :param faker: An instance of faker.
    :param lt: Less than value.
    :param le: Less than or equal value.
    :param gt: Greater than value.
    :param ge: Greater than or equal value.
    :param tz: A timezone. When a boolean is passed (as used by ``msgspec.Meta``),
        ``True`` maps to ``timezone.utc`` (timezone-aware) and ``False`` maps to
        ``None`` (timezone-naive). If any bound is given, its timezone is used instead so that
        the generated value can be compared with the bounds.

    :returns: A datetime instance.
    """
    if isinstance(tz, bool):
        tz = timezone.utc if tz else None

    bound = next((value for value in (ge, gt, le, lt) if value is not None), None)
    if bound is not None:
        tz = bound.tzinfo

    start_datetime = datetime.now(tz=tz) - timedelta(days=100)
    if ge is not None:
        start_datetime = ge
    elif gt is not None:
        start_datetime = gt + timedelta(seconds=1)

    end_datetime = datetime.now(tz=tz) + timedelta(days=100)
    if le is not None:
        end_datetime = le
    elif lt is not None:
        end_datetime = lt - timedelta(seconds=1)

    if ge is None and gt is None and start_datetime > end_datetime:
        start_datetime = end_datetime - timedelta(days=200)
    elif le is None and lt is None and end_datetime < start_datetime:
        end_datetime = start_datetime + timedelta(days=200)

    seconds = faker.random.uniform(0, max((end_datetime - start_datetime).total_seconds(), 0))
    return start_datetime + timedelta(seconds=seconds)
