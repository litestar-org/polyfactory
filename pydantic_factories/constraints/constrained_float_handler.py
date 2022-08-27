from typing import TYPE_CHECKING

from pydantic_factories.value_generators.constrained_number import (
    generate_constrained_number,
    get_constrained_number_range,
)
from pydantic_factories.value_generators.primitives import create_random_float

if TYPE_CHECKING:
    from pydantic import ConstrainedFloat


def handle_constrained_float(field: "ConstrainedFloat") -> float:
    """Handles 'ConstrainedFloat' instances."""
    multiple_of = field.multiple_of
    if multiple_of == 0:
        return 0
    minimum, maximum = get_constrained_number_range(
        gt=field.gt, ge=field.ge, lt=field.lt, le=field.le, t_type=float, multiple_of=multiple_of
    )
    return generate_constrained_number(
        minimum=minimum,
        maximum=maximum,
        multiple_of=multiple_of,
        method=create_random_float,
    )
