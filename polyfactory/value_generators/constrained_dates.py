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
        ``None`` (timezone-naive), matching the semantics of ``msgspec.Meta(tz=...)``.

    :returns: A datetime instance.
    """
    if isinstance(tz, bool):
        tz = timezone.utc if tz else None

    start_dt = datetime.now(tz=tz) - timedelta(days=100)
    if ge:
        start_dt = ge
    elif gt:
        start_dt = gt + timedelta(days=1)

    end_dt = datetime.now(tz=tz) + timedelta(days=100)
    if le:
        end_dt = le
    elif lt:
        end_dt = lt - timedelta(days=1)

    # faker and the validated model both reject comparisons between
    # timezone-aware and timezone-naive datetimes, so the default bounds adopt
    # the awareness of the given constraints.
    constraints = [c for c in (ge, gt, le, lt) if c is not None]
    if constraints:
        target_tz = constraints[0].tzinfo
        if (start_dt.tzinfo is None) != (target_tz is None):
            start_dt = start_dt.replace(tzinfo=target_tz)
        if (end_dt.tzinfo is None) != (target_tz is None):
            end_dt = end_dt.replace(tzinfo=target_tz)

    return faker.date_time_between(start_date=start_dt, end_date=end_dt, tzinfo=start_dt.tzinfo)
