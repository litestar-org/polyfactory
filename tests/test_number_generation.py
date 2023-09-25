from random import Random

import pytest

from polyfactory.value_generators.constrained_numbers import (
    generate_constrained_number,
    passes_pydantic_multiple_validator,
)
from polyfactory.value_generators.primitives import create_random_float


@pytest.mark.parametrize(
    ("maximum", "minimum", "multiple_of"),
    ((100, 2, 8), (-100, -187, -10), (7.55, 0.13, 0.0123)),
)
def test_generate_constrained_number(maximum: float, minimum: float, multiple_of: float) -> None:
    assert passes_pydantic_multiple_validator(
        multiple_of=multiple_of,
        value=generate_constrained_number(
            random=Random(),
            minimum=minimum,
            maximum=maximum,
            multiple_of=multiple_of,
            method=create_random_float,
        ),
    )


def test_passes_pydantic_multiple_validator_handles_zero_multiplier() -> None:
    assert passes_pydantic_multiple_validator(1.0, 0)
