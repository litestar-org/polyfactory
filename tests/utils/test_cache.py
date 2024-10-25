from dataclasses import dataclass
from typing import Set

from polyfactory.factories.dataclass_factory import DataclassFactory
from polyfactory.utils.cache import copying_lru_cache


def test_copying_lru_cache_copies() -> None:
    @copying_lru_cache
    def f() -> Set[str]:
        return {"foo"}

    result = f()
    result.add("bar")
    assert f() == {"foo"}


def test_cached_per_class() -> None:
    class A:
        @classmethod
        @copying_lru_cache
        def name(cls) -> str:
            return cls.__name__

    class B(A): ...

    assert A.name() == "A"
    assert B.name() == "B"


def test_resetting_random_resets_cache() -> None:
    @dataclass
    class A:
        a: str

    class Factory(DataclassFactory[A]): ...

    Factory.seed_random(1)
    first_result = Factory.build().a
    second_result = Factory.build().a
    assert first_result != second_result

    Factory.seed_random(1)
    after_reset = Factory.build().a
    assert first_result == after_reset
