from typing import Any

import pytest
from _pytest.fixtures import FixtureRequest
from _pytest.monkeypatch import MonkeyPatch

from polyfactory.field_meta import FieldMeta


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
