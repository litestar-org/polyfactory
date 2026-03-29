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
    :param tz: A timezone. If a bool is passed (e.g. from msgspec Meta(tz=True)),
        True is converted to UTC and False to None.

    :returns: A date instance.
    """
    # Handle boolean tz values from msgspec's Meta constraint
    if isinstance(tz, bool):
        tz = timezone.utc if tz else None
    elif tz is None:
        tz = timezone.utc
    start_date = datetime.now(tz=tz).date() - timedelta(days=100)
    if ge:
        start_date = ge
    elif gt:
        start_date = gt + timedelta(days=1)

    end_date = datetime.now(tz=timezone.utc).date() + timedelta(days=100)
    if le:
        end_date = le
    elif lt:
        end_date = lt - timedelta(days=1)

    return faker.date_between(start_date=start_date, end_date=end_date)
