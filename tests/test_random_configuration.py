from dataclasses import dataclass
from random import Random
from typing import List, Union

import pytest
from faker import Faker
from faker.config import AVAILABLE_LOCALES

from polyfactory.factories.dataclass_factory import DataclassFactory

FakerLocaleType = Union[str, List[str]]

RANDINT_MAP = {i: Random(i).randint(0, 10) for i in range(3)}
FAKER_LOCALES: List[FakerLocaleType] = [
    AVAILABLE_LOCALES[0],
    AVAILABLE_LOCALES[1],
    AVAILABLE_LOCALES[2],
    AVAILABLE_LOCALES[:3],
]


@pytest.mark.parametrize("seed", RANDINT_MAP.keys())
def test_setting_random(seed: int) -> None:
    @dataclass
    class Foo:
        foo: int

    class FooFactory(DataclassFactory[Foo]):
        __model__ = Foo
        __random__ = Random(seed)

        @classmethod
        def foo(cls) -> int:
            return cls.__random__.randint(0, 10)

    assert FooFactory.build().foo == RANDINT_MAP[seed]


@pytest.mark.parametrize("seed", RANDINT_MAP.keys())
def test_setting_random_seed_on_random(seed: int) -> None:
    @dataclass
    class Foo:
        foo: int

    class FooFactory(DataclassFactory[Foo]):
        __model__ = Foo
        __random_seed__ = seed

        @classmethod
        def foo(cls) -> int:
            return cls.__random__.randint(0, 10)

    assert FooFactory.build().foo == RANDINT_MAP[seed]


@pytest.mark.parametrize("seed", RANDINT_MAP.keys())
def test_setting_random_seed_on_faker(seed: int) -> None:
    @dataclass
    class Foo:
        foo: int

    class FooFactory(DataclassFactory[Foo]):
        __model__ = Foo
        __random_seed__ = seed

        @classmethod
        def foo(cls) -> int:
            return cls.__faker__.random_digit()

    assert FooFactory.build().foo == RANDINT_MAP[seed]


def test_setting_random_seed_on_multiple_factories() -> None:
    foo_seed = 0
    bar_seed = 1

    @dataclass
    class Foo:
        foo: int

    @dataclass
    class Bar:
        bar: int

    class FooFactory(DataclassFactory[Foo]):
        __model__ = Foo
        __random_seed__ = foo_seed

        @classmethod
        def foo(cls) -> int:
            return cls.__random__.randint(0, 10)

    class BarFactory(DataclassFactory[Bar]):
        __model__ = Bar
        __random_seed__ = bar_seed

        @classmethod
        def bar(cls) -> int:
            return cls.__random__.randint(0, 10)

    assert FooFactory.build().foo == RANDINT_MAP[foo_seed]
    assert BarFactory.build().bar == RANDINT_MAP[bar_seed]


def test_no_override_of_faker() -> None:
    faker = Faker()

    @dataclass
    class Foo:
        foo: int

    class FooFactory(DataclassFactory[Foo]):
        __model__ = Foo

        __faker__ = faker
        __random_seed__ = 10

    assert FooFactory.__faker__ is faker


@pytest.mark.parametrize("locale", FAKER_LOCALES)
def test_faker_locale_preserved(locale: FakerLocaleType) -> None:
    @dataclass
    class Foo:
        foo: int

    class FooFactory(DataclassFactory[Foo]):
        __model__ = Foo

        __faker__ = Faker(locale=locale)
        __random_seed__ = 10

    expected_locales = [locale] if isinstance(locale, str) else locale

    assert FooFactory.__faker__.locales == expected_locales
