from __future__ import annotations

import pytest

from polyfactory.utils.deprecation import check_for_deprecated_parameters


def test_parameter_deprecation() -> None:
    def my_func(a: int, b: int | None = None) -> None:
        check_for_deprecated_parameters("5", parameters=(("b", b),))

    with pytest.warns(
        DeprecationWarning,
        match="Use of deprecated parameter 'b'. Deprecated in polyfactory 5. This parameter will be removed in the next major version",
    ):
        my_func(1, 2)
