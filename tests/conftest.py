import random

import pytest
from _pytest.fixtures import FixtureRequest
from _pytest.monkeypatch import MonkeyPatch

from polyfactory import BaseFactory


@pytest.fixture(autouse=True)
def constant_length_type_args(request: FixtureRequest, monkeypatch: MonkeyPatch) -> None:
    """
    Make sure that the length of the type_args tuple is always 1.
    """
    if "enable_randint" not in request.keywords:
        monkeypatch.setattr(BaseFactory.__random__, random.randint.__name__, lambda _, __: 1)
