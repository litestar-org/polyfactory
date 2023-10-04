from __future__ import annotations

import sys
from dataclasses import dataclass
from datetime import date
from typing import Literal, Sequence
from uuid import UUID

import pytest
from typing_extensions import TypedDict

from polyfactory.decorators import post_generated
from polyfactory.factories.dataclass_factory import DataclassFactory
from polyfactory.factories.typed_dict_factory import TypedDictFactory


@pytest.mark.skipif(sys.version_info < (3, 10), reason="requires python3.10 or higher")
def test_coverage_count() -> None:
    @dataclass
    class Profile:
        name: str
        high_score: int | float
        dob: date
        data: str | date | int | float

    class ProfileFactory(DataclassFactory[Profile]):
        __model__ = Profile

    results = list(ProfileFactory.coverage())

    assert len(results) == 4

    for result in results:
        assert isinstance(result, Profile)


@pytest.mark.skipif(sys.version_info < (3, 10), reason="requires python3.10 or higher")
def test_coverage_tuple() -> None:
    @dataclass
    class Tuple:
        tuple_: tuple[int | str, tuple[int | float, int]]

    class TupleFactory(DataclassFactory[Tuple]):
        __model__ = Tuple

    results = list(TupleFactory.coverage())

    assert len(results) == 2

    a0, (b0, c0) = results[0].tuple_
    a1, (b1, c1) = results[1].tuple_

    assert isinstance(a0, int) and isinstance(b0, int) and isinstance(c0, int)
    assert isinstance(a1, str) and isinstance(b1, float) and isinstance(c1, int)


@pytest.mark.skipif(sys.version_info < (3, 10), reason="requires python3.10 or higher")
def test_coverage_collection() -> None:
    @dataclass
    class Collective:
        set_: set[int | str]
        list_: list[int | str]
        frozenset_: frozenset[int | str]
        sequence_: Sequence[int | str]

    class CollectiveFactory(DataclassFactory[Collective]):
        __model__ = Collective

    results = list(CollectiveFactory.coverage())

    assert len(results) == 1

    result = results[0]

    assert len(result.set_) == 2
    assert len(result.list_) == 2
    assert len(result.frozenset_) == 2
    assert len(result.sequence_) == 2

    v0, v1 = result.set_
    assert {type(v0), type(v1)} == {int, str}
    v0, v1 = result.list_
    assert {type(v0), type(v1)} == {int, str}
    v0, v1 = result.frozenset_
    assert {type(v0), type(v1)} == {int, str}
    v0, v1 = result.sequence_
    assert {type(v0), type(v1)} == {int, str}


@pytest.mark.skipif(sys.version_info < (3, 10), reason="requires python3.10 or higher")
def test_coverage_literal() -> None:
    @dataclass
    class Literally:
        literal: Literal["a", "b", 1, 2]

    class LiterallyFactory(DataclassFactory[Literally]):
        __model__ = Literally

    results = list(LiterallyFactory.coverage())

    assert len(results) == 4

    assert results[0].literal == "a"
    assert results[1].literal == "b"
    assert results[2].literal == 1
    assert results[3].literal == 2


@pytest.mark.skipif(sys.version_info < (3, 10), reason="requires python3.10 or higher")
def test_coverage_dict() -> None:
    @dataclass
    class Thesaurus:
        dict_simple: dict[str, int]
        dict_more_key_types: dict[str | int | float, int | str]
        dict_more_value_types: dict[str, int | str]

    class ThesaurusFactory(DataclassFactory[Thesaurus]):
        __model__ = Thesaurus

    results = list(ThesaurusFactory.coverage())

    assert len(results) == 3


@pytest.mark.skip(reason="Does not support recursive types yet.")
@pytest.mark.skipif(sys.version_info < (3, 10), reason="requires python3.10 or higher")
def test_coverage_recursive() -> None:
    @dataclass
    class Recursive:
        r: Recursive | None

    class RecursiveFactory(DataclassFactory[Recursive]):
        __model__ = Recursive

    results = list(RecursiveFactory.coverage())
    assert len(results) == 2


@pytest.mark.skipif(sys.version_info < (3, 10), reason="requires python3.10 or higher")
def test_coverage_typed_dict() -> None:
    class TypedThesaurus(TypedDict):
        number: int
        string: str
        union: int | str
        collection: list[int | str]

    class TypedThesaurusFactory(TypedDictFactory[TypedThesaurus]):
        __model__ = TypedThesaurus

    results = list(TypedThesaurusFactory.coverage())

    assert len(results) == 2

    example = TypedThesaurusFactory.build()
    for result in results:
        assert result.keys() == example.keys()


@pytest.mark.skipif(sys.version_info < (3, 10), reason="requires python3.10 or higher")
def test_coverage_typed_dict_field() -> None:
    class TypedThesaurus(TypedDict):
        number: int
        string: str
        union: int | str
        collection: list[int | str]

    class TypedThesaurusFactory(TypedDictFactory[TypedThesaurus]):
        __model__ = TypedThesaurus

    results = list(TypedThesaurusFactory.coverage())

    assert len(results) == 2

    example = TypedThesaurusFactory.build()

    for result in results:
        assert result.keys() == example.keys()


@pytest.mark.skipif(sys.version_info < (3, 10), reason="requires python3.10 or higher")
def test_coverage_values_unique() -> None:
    @dataclass
    class Unique:
        uuid: UUID
        data: int | str

    class UniqueFactory(DataclassFactory[Unique]):
        __model__ = Unique

    results = list(UniqueFactory.coverage())

    assert len(results) == 2
    assert results[0].uuid != results[1].uuid


@pytest.mark.skipif(sys.version_info < (3, 10), reason="requires python3.10 or higher")
def test_coverage_post_generated() -> None:
    @dataclass
    class Model:
        i: int
        j: int

    class Factory(DataclassFactory[Model]):
        __model__ = Model

        @post_generated
        @classmethod
        def i(cls, j: int) -> int:
            return j + 10

    results = list(Factory.coverage())
    assert len(results) == 1

    assert results[0].i == results[0].j + 10
