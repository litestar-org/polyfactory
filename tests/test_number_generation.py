from polyfactory.value_generators.constrained_numbers import (
    is_almost_multiple_of,
)


def test_is_close_enough_multiple_of_handles_zero_multiplier() -> None:
    assert is_almost_multiple_of(1.0, 0)
