from __future__ import annotations

import sys
from datetime import date
from typing import Literal, Sequence
from uuid import UUID

import pytest
from pydantic import BaseModel
from typing_extensions import TypedDict

from polyfactory.factories.pydantic_factory import ModelFactory
from polyfactory.factories.typed_dict_factory import TypedDictFactory


@pytest.mark.skipif(sys.version_info < (3, 10), reason="requires python3.10 or higher")
def test_coverage_count() -> None:
    class Stringy(BaseModel):
        string: str

    class Numberish(BaseModel):
        number: int | float

    class Datelike(BaseModel):
        birthday: date

    class Profile(BaseModel):
        name: Stringy
        high_score: Numberish
        dob: Datelike
        data: Stringy | Datelike | Numberish

    class ProfileFactory(ModelFactory[Profile]):
        __model__ = Profile

    results = list(ProfileFactory.coverage())

    assert len(results) == 4

    for result in results:
        assert isinstance(result, Profile)


@pytest.mark.skipif(sys.version_info < (3, 10), reason="requires python3.10 or higher")
def test_coverage_tuple() -> None:
    class Numberish(BaseModel):
        number: int | float

    class Tuple(BaseModel):
        tuple_: tuple[int | str, tuple[Numberish, int]]

    class TupleFactory(ModelFactory[Tuple]):
        __model__ = Tuple

    results = list(TupleFactory.coverage())

    assert len(results) == 2

    a0, (b0, c0) = results[0].tuple_
    a1, (b1, c1) = results[1].tuple_

    assert isinstance(a0, int) and isinstance(b0, Numberish) and isinstance(b0.number, int) and isinstance(c0, int)
    assert isinstance(a1, str) and isinstance(b1, Numberish) and isinstance(b1.number, float) and isinstance(c1, int)


@pytest.mark.skipif(sys.version_info < (3, 10), reason="requires python3.10 or higher")
def test_coverage_collection() -> None:
    class Collective(BaseModel):
        set_: set[int | str]
        list_: list[int | str]
        frozenset_: frozenset[int | str]
        sequence_: Sequence[int | str]

    class CollectiveFactory(ModelFactory[Collective]):
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
    class Literally(BaseModel):
        literal: Literal["a", "b", 1, 2]

    class LiterallyFactory(ModelFactory[Literally]):
        __model__ = Literally

    results = list(LiterallyFactory.coverage())

    assert len(results) == 4

    assert results[0].literal == "a"
    assert results[1].literal == "b"
    assert results[2].literal == 1
    assert results[3].literal == 2


def test_coverage_dict() -> None:
    class Thesaurus(BaseModel):
        dict_simple: dict[str, int]
        dict_more_key_types: dict[str | int | float, int | str]
        dict_more_value_types: dict[str, int | str]

    class ThesaurusFactory(ModelFactory[Thesaurus]):
        __model__ = Thesaurus

    results = list(ThesaurusFactory.coverage())

    assert len(results) == 3


@pytest.mark.skip(reason="Does not support recursive types yet.")
@pytest.mark.skipif(sys.version_info < (3, 10), reason="requires python3.10 or higher")
def test_coverage_recursive() -> None:
    class Recursive(BaseModel):
        r: Recursive | None

    class RecursiveFactory(ModelFactory[Recursive]):
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

    class TypedThesaurusModel(BaseModel):
        thesaurus: TypedThesaurus

    class TypedThesaurusModelFactory(ModelFactory[TypedThesaurusModel]):
        __model__ = TypedThesaurusModel

    class TypedThesaurusFactory(TypedDictFactory[TypedThesaurus]):
        __model__ = TypedThesaurus

    results = list(TypedThesaurusModelFactory.coverage())

    assert len(results) == 2

    example = TypedThesaurusFactory.build()

    for result in results:
        assert result.thesaurus.keys() == example.keys()


@pytest.mark.skipif(sys.version_info < (3, 10), reason="requires python3.10 or higher")
def test_coverage_values_unique() -> None:
    class Unique(BaseModel):
        uuid: UUID
        data: int | str

    class UniqueFactory(ModelFactory[Unique]):
        __model__ = Unique

    results = list(UniqueFactory.coverage())

    assert len(results) == 2
    assert results[0].uuid != results[1].uuid
