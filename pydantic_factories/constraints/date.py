from datetime import date, timedelta
from typing import TYPE_CHECKING, cast

if TYPE_CHECKING:
    from faker import Faker
    from pydantic import ConstrainedDate


def handle_constrained_date(constrained_date: "ConstrainedDate", faker: "Faker") -> date:
    """
    Generates a date value fulfilling the expected constraints.
    Args:
        constrained_date:
        faker:

    Returns:

    """
    start_date = date.today() - timedelta(days=100)
    if constrained_date.ge:
        start_date = constrained_date.ge
    elif constrained_date.gt:
        start_date = constrained_date.gt + timedelta(days=1)

    end_date = date.today() + timedelta(days=100)
    if constrained_date.le:
        end_date = constrained_date.le
    elif constrained_date.lt:
        end_date = constrained_date.lt - timedelta(days=1)

    return cast("date", faker.date_between(start_date=start_date, end_date=end_date))
