# ruff: noqa: UP007, UP006
from __future__ import annotations

from dataclasses import dataclass, make_dataclass
from datetime import date
from typing import Dict, FrozenSet, List, Literal, Optional, Set, Tuple, Union
from uuid import UUID

import pytest
from typing_extensions import TypedDict

from polyfactory.decorators import post_generated
from polyfactory.exceptions import ParameterException
from polyfactory.factories.dataclass_factory import DataclassFactory
from polyfactory.factories.typed_dict_factory import TypedDictFactory


def test_coverage_count() -> None:
    @dataclass
    class Profile:
        name: str
        high_score: Union[int, float]
        dob: date
        data: Union[str, date, int, float]

    class ProfileFactory(DataclassFactory[Profile]):
        __model__ = Profile

    results = list(ProfileFactory.coverage())

    assert len(results) == 4

    for result in results:
        assert isinstance(result, Profile)


def test_coverage_tuple() -> None:
    @dataclass
    class Pair:
        tuple_: Tuple[Union[int, str], Tuple[Union[int, float], int]]

    class TupleFactory(DataclassFactory[Pair]):
        __model__ = Pair

    results = list(TupleFactory.coverage())

    assert len(results) == 2

    a0, (b0, c0) = results[0].tuple_
    a1, (b1, c1) = results[1].tuple_

    assert isinstance(a0, int) and isinstance(b0, int) and isinstance(c0, int)
    assert isinstance(a1, str) and isinstance(b1, float) and isinstance(c1, int)


@pytest.mark.parametrize(
    "collection_annotation",
    (Set[Union[int, str]], List[Union[int, str]], FrozenSet[Union[int, str]]),
)
def test_coverage_collection(collection_annotation: type) -> None:
    Collective = make_dataclass("Collective", [("collection", collection_annotation)])

    class CollectiveFactory(DataclassFactory[Collective]):  # type: ignore
        __model__ = Collective

    results = list(CollectiveFactory.coverage())

    assert len(results) == 1

    result = results[0]

    collection = result.collection  # type: ignore

    assert len(collection) == 2

    v0, v1 = collection
    assert {type(v0), type(v1)} == {int, str}


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


def test_coverage_dict() -> None:
    @dataclass
    class Thesaurus:
        dict_simple: Dict[str, int]
        dict_more_key_types: Dict[Union[str, int, float], Union[int, str]]
        dict_more_value_types: Dict[str, Union[int, str]]

    class ThesaurusFactory(DataclassFactory[Thesaurus]):
        __model__ = Thesaurus

    results = list(ThesaurusFactory.coverage())

    assert len(results) == 3


@pytest.mark.skip(reason="Does not support recursive types yet.")
def test_coverage_recursive() -> None:
    @dataclass
    class Recursive:
        r: Union[Recursive, None]

    class RecursiveFactory(DataclassFactory[Recursive]):
        __model__ = Recursive

    results = list(RecursiveFactory.coverage())
    assert len(results) == 2


def test_coverage_typed_dict() -> None:
    class TypedThesaurus(TypedDict):
        number: int
        string: str
        union: Union[int, str]
        collection: List[Union[int, str]]

    class TypedThesaurusFactory(TypedDictFactory[TypedThesaurus]):
        __model__ = TypedThesaurus

    results = list(TypedThesaurusFactory.coverage())

    assert len(results) == 2

    example = TypedThesaurusFactory.build()
    for result in results:
        assert result.keys() == example.keys()


def test_coverage_typed_dict_field() -> None:
    class TypedThesaurus(TypedDict):
        number: int
        string: str
        union: Union[int, str]
        collection: List[Union[int, str]]

    class TypedThesaurusFactory(TypedDictFactory[TypedThesaurus]):
        __model__ = TypedThesaurus

    results = list(TypedThesaurusFactory.coverage())

    assert len(results) == 2

    example = TypedThesaurusFactory.build()

    for result in results:
        assert result.keys() == example.keys()


def test_coverage_values_unique() -> None:
    @dataclass
    class Unique:
        uuid: UUID
        data: Union[int, str]

    class UniqueFactory(DataclassFactory[Unique]):
        __model__ = Unique

    results = list(UniqueFactory.coverage())

    assert len(results) == 2
    assert results[0].uuid != results[1].uuid


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


class CustomInt:
    def __init__(self, value: int) -> None:
        self.value = value


def test_coverage_parameter_exception() -> None:
    @dataclass
    class Model:
        i: CustomInt

    class Factory(DataclassFactory[Model]):
        __model__ = Model

    with pytest.raises(ParameterException):
        list(Factory.coverage())


def test_coverage_optional_field() -> None:
    @dataclass
    class OptionalInt:
        i: Optional[int]

    class OptionalIntFactory(DataclassFactory[OptionalInt]):
        __model__ = OptionalInt

    results = list(OptionalIntFactory.coverage())
    assert len(results) == 2

    assert isinstance(results[0].i, int)
    assert results[1].i is None
