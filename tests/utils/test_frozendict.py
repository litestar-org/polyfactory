import pytest

from polyfactory.utils.types import Frozendict


def test_frozendict_immutable() -> None:
    instance = Frozendict()
    with pytest.raises(TypeError, match="Unable to set value"):
        instance["foo"] = "bar"


def test_frozendict_hashable() -> None:
    assert isinstance(hash(Frozendict()), int)
