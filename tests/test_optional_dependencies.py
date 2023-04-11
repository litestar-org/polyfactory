from unittest import mock

import pytest


@pytest.mark.parametrize("module_name", ["beanie", "pydantic", "odmatic"])
def test_missing_dependency(module_name: str) -> None:
    with mock.patch.dict("sys.modules", {module_name: None}):
        import polyfactory.factories.base  # noqa: F401
