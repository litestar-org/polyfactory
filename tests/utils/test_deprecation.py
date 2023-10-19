import pytest

from polyfactory.utils.deprecation import deprecated_parameter


def test_parameter_deprecation() -> None:
    def my_func(a: int, b: int | None = None) -> None:
        deprecated_parameter("5", parameters=(("b", b),))

    with pytest.warns(
        DeprecationWarning,
        match="Use of deprecated parameter 'b'. Deprecated in polyfactory 5. This parameter will be removed in the next major version",
    ):
        my_func(1, 2)
