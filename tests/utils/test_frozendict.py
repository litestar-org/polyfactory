import pytest

from polyfactory.utils.types import Frozendict


def test_frozendict_immutable() -> None:
    instance = Frozendict({"bar": "foo"})
    with pytest.raises(TypeError, match="Unable to mutate Frozendict"):
        instance["foo"] = "bar"


def test_frozendict_hashable() -> None:
    assert isinstance(hash(Frozendict()), int)
