from __future__ import annotations

import importlib.util
import random
import string
import sys
from typing import TYPE_CHECKING, Any, TypeVar

import pytest

from polyfactory.field_meta import FieldMeta

if TYPE_CHECKING:
    from pathlib import Path
    from types import ModuleType
    from typing import Callable

    from pytest import FixtureRequest, MonkeyPatch


T = TypeVar("T")


@pytest.fixture
def create_module(tmp_path: Path, monkeypatch: MonkeyPatch) -> Callable[[str], ModuleType]:
    """Utility fixture for dynamic module creation."""

    def wrapped(source: str) -> ModuleType:
        """

        Args:
            source: Source code as a string.

        Returns:
            An imported module.
        """

        def not_none(val: T | None) -> T:
            assert val is not None
            return val

        def module_name_generator() -> str:
            letters = string.ascii_lowercase
            return "".join(random.choice(letters) for _ in range(10))

        module_name = module_name_generator()
        path = tmp_path / f"{module_name}.py"
        path.write_text(source)
        # https://docs.python.org/3/library/importlib.html#importing-a-source-file-directly
        spec = not_none(importlib.util.spec_from_file_location(module_name, path))
        module = not_none(importlib.util.module_from_spec(spec))
        monkeypatch.setitem(sys.modules, module_name, module)
        not_none(spec.loader).exec_module(module)
        return module

    return wrapped


@pytest.fixture(autouse=True)
def mock_random_in_field_meta(request: FixtureRequest, monkeypatch: MonkeyPatch) -> None:
    """
    Mock randint only in FieldMeta.from_type
    """
    if "enable_randint" in request.keywords:
        return

    class NotSoRandom:
        @staticmethod
        def randint(_: int, __: int) -> int:
            return 1

    original_from_type = FieldMeta.from_type

    def from_type_mock(*args: Any, **kwargs: Any) -> FieldMeta:
        kwargs["random_"] = NotSoRandom
        return original_from_type(*args, **kwargs)

    monkeypatch.setattr(FieldMeta, FieldMeta.from_type.__name__, from_type_mock)
