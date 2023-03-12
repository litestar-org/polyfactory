from datetime import timedelta, timezone, datetime
from typing import TYPE_CHECKING, Optional, cast

if TYPE_CHECKING:
    from faker import Faker


def handle_constrained_date(
    faker: "Faker",
    ge: Optional[datetime] = None,
    gt: Optional[datetime] = None,
    le: Optional[datetime] = None,
    lt: Optional[datetime] = None,
) -> datetime:
    """Generates a date value fulfilling the expected constraints.

    :param faker: An instance of faker.
    :param lt: Less than value.
    :param le: Less than or equal value.
    :param gt: Greater than value.
    :param ge: Greater than or equal value.

    :returns: A date instance.
    """
    start_date = datetime.now(tz=timezone.utc) - timedelta(days=100)
    if ge:
        start_date = ge
    elif gt:
        start_date = gt + timedelta(days=1)

    end_date = datetime.now(tz=timezone.utc) + timedelta(days=100)
    if le:
        end_date = le
    elif lt:
        end_date = lt - timedelta(days=1)

    return cast("datetime", faker.date_between(start_date=start_date, end_date=end_date))
