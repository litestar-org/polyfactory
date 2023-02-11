from datetime import date, timedelta
from typing import TYPE_CHECKING, Optional, cast

if TYPE_CHECKING:
    from faker import Faker


def handle_constrained_date(
    faker: "Faker",
    ge: Optional[date] = None,
    gt: Optional[date] = None,
    le: Optional[date] = None,
    lt: Optional[date] = None,
) -> date:
    """Generates a date value fulfilling the expected constraints.
    :param faker:
    :param ge:
    :param gt:
    :param le:
    :param lt:
    :return:
    """
    start_date = date.today() - timedelta(days=100)
    if ge:
        start_date = ge
    elif gt:
        start_date = gt + timedelta(days=1)

    end_date = date.today() + timedelta(days=100)
    if le:
        end_date = le
    elif lt:
        end_date = lt - timedelta(days=1)

    return cast("date", faker.date_between(start_date=start_date, end_date=end_date))
