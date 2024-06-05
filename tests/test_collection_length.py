from typing import Any, Dict, List, Optional, Set, Tuple

import pytest

from pydantic.dataclasses import dataclass

from polyfactory.factories import DataclassFactory

MIN_MAX_PARAMETERS = ((10, 15), (20, 25), (30, 40), (40, 50))


@pytest.mark.parametrize("type_", (List, Set))
@pytest.mark.parametrize(("min_val", "max_val"), MIN_MAX_PARAMETERS)
def test_collection_length_with_list(min_val: int, max_val: int, type_: type) -> None:
    @dataclass
    class Foo:
        foo: type_[int]  # type: ignore

    class FooFactory(DataclassFactory[Foo]):
        __model__ = Foo
        __randomize_collection_length__ = True
        __min_collection_length__ = min_val
        __max_collection_length__ = max_val

    foo = FooFactory.build()

    assert len(foo.foo) >= min_val, len(foo.foo)
    assert len(foo.foo) <= max_val, len(foo.foo)


def test_collection_length_with_set_collision() -> None:
    @dataclass
    class Foo:
        foo: Set[int]

    provider_int_values_reversed = (list(range(9)) + list(range(7, 15)))[::-1]

    class FooFactory(DataclassFactory[Foo]):
        __model__ = Foo
        __randomize_collection_length__ = True
        __min_collection_length__ = 10
        __max_collection_length__ = 10

        @classmethod
        def get_provider_map(cls) -> Dict[Any, Any]:
            providers_map = super().get_provider_map()
            providers_map[int] = lambda: provider_int_values_reversed.pop()
            return providers_map

    foo = FooFactory.build()

    assert len(foo.foo) >= 10, len(foo.foo)
    assert len(foo.foo) <= 15, len(foo.foo)


@pytest.mark.parametrize(("min_val", "max_val"), MIN_MAX_PARAMETERS)
def test_collection_length_with_tuple(min_val: int, max_val: int) -> None:
    @dataclass
    class Foo:
        foo: Tuple[int, ...]

    class FooFactory(DataclassFactory[Foo]):
        __model__ = Foo
        __randomize_collection_length__ = True
        __min_collection_length__ = min_val
        __max_collection_length__ = max_val

    foo = FooFactory.build()

    assert len(foo.foo) >= min_val, len(foo.foo)
    assert len(foo.foo) <= max_val, len(foo.foo)


@pytest.mark.parametrize(("min_val", "max_val"), MIN_MAX_PARAMETERS)
def test_collection_length_with_dict(min_val: int, max_val: int) -> None:
    @dataclass
    class Foo:
        foo: Dict[int, int]

    class FooFactory(DataclassFactory[Foo]):
        __model__ = Foo

        __randomize_collection_length__ = True
        __min_collection_length__ = min_val
        __max_collection_length__ = max_val

    foo = FooFactory.build()

    assert len(foo.foo) >= min_val, len(foo.foo)
    assert len(foo.foo) <= max_val, len(foo.foo)


@pytest.mark.parametrize(("min_val", "max_val"), MIN_MAX_PARAMETERS)
def test_collection_length_with_optional_not_allowed(min_val: int, max_val: int) -> None:
    @dataclass
    class Foo:
        foo: Optional[List[int]]

    class FooFactory(DataclassFactory[Foo]):
        __model__ = Foo

        __allow_none_optionals__ = False
        __randomize_collection_length__ = True
        __min_collection_length__ = min_val
        __max_collection_length__ = max_val

    foo = FooFactory.build()

    assert foo.foo is not None
    assert len(foo.foo) >= min_val, len(foo.foo)
    assert len(foo.foo) <= max_val, len(foo.foo)


@pytest.mark.parametrize(("min_val", "max_val"), MIN_MAX_PARAMETERS)
def test_collection_length_with_optional_allowed(min_val: int, max_val: int) -> None:
    @dataclass
    class Foo:
        foo: Optional[List[int]]

    class FooFactory(DataclassFactory[Foo]):
        __model__ = Foo

        __randomize_collection_length__ = True
        __min_collection_length__ = min_val
        __max_collection_length__ = max_val

    for _ in range(10):
        foo = FooFactory.build()

        if foo.foo is None:
            continue

        assert len(foo.foo) >= min_val, len(foo.foo)
        assert len(foo.foo) <= max_val, len(foo.foo)
