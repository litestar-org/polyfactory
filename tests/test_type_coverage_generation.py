# ruff: noqa: UP007, UP006
from __future__ import annotations

from dataclasses import dataclass, make_dataclass
from datetime import date
from typing import Any, Dict, FrozenSet, Iterable, List, Literal, Optional, Set, Tuple, Type, Union
from uuid import UUID

import pytest
from typing_extensions import TypedDict

from pydantic import BaseModel

from polyfactory.decorators import post_generated
from polyfactory.exceptions import ParameterException
from polyfactory.factories.dataclass_factory import DataclassFactory
from polyfactory.factories.pydantic_factory import ModelFactory
from polyfactory.factories.typed_dict_factory import TypedDictFactory
from polyfactory.utils.types import NoneType
from tests.test_pydantic_factory import IS_PYDANTIC_V1


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


def type_exists_at_path_any(objs: Iterable, path: List[Union[int, str]], target_type: Type) -> bool:
    return any(type_exists_at_path(obj, path, target_type) for obj in objs)


def type_exists_at_path(obj: Any, path: List[Union[int, str]], target_type: Type) -> bool:
    """Determine if a type exists at a path through a given object

        type_exists_at_path(obj, ["i", "*"], int)
        returns true if 'obj' contains an iterable attribute called 'i' with an 'int' value
        '*' is used to mean any of an iterable

        type_exists_at_path(obj, ["i", 5], int)
        returns true if 'obj' contains an iterable attribute called 'i' with an 'int' value at the index 5
        Direct indexing is useful for checking tuples

    :param obj: Object to search through
    :param path: List of either indexes or attr keys to dereferrence
    :param target_type: Type to match

    :returns: A boolean, True if the type exists at the path, False otherwise
    """
    # Handle fully dereferenced item and the end of path
    if len(path) == 0:
        return type(obj) == target_type

    if path[0] == "*":
        if not isinstance(obj, Iterable):
            return False
        for piece in obj:
            if type_exists_at_path(piece, path[1:], target_type):
                return True
        return False

    item, success = get_or_index(obj, path[0])
    if not success:
        return False

    return type_exists_at_path(item, path[1:], target_type)


def get_or_index(obj: Any, idx: Union[int, str]) -> Tuple[Any, bool]:
    if isinstance(idx, str):
        if idx not in dir(obj):
            return None, False

        return getattr(obj, idx), True
    if len(obj) < idx:
        return None, False

    return obj[idx], True


def test_coverage_optional_list() -> None:
    @dataclass
    class OptionalIntList:
        i: Optional[List[int]]

    class OptionalIntFactory(DataclassFactory[OptionalIntList]):
        __model__ = OptionalIntList

    results = list(OptionalIntFactory.coverage())

    assert type_exists_at_path_any(results, ["i"], list)
    assert type_exists_at_path_any(results, ["i", "*"], int)
    assert type_exists_at_path_any(results, ["i"], NoneType)


def test_optional_lists() -> None:
    class Model(BaseModel):
        just_a_list: List[int]
        optional_list: Optional[List[int]]
        optional_nested_list: Optional[List[List[List[int]]]]

    results = list(ModelFactory.create_factory(Model).coverage())
    assert type_exists_at_path_any(results, ["just_a_list"], list)
    assert type_exists_at_path_any(results, ["optional_list"], list)
    assert type_exists_at_path_any(results, ["optional_list"], NoneType)
    assert type_exists_at_path_any(results, ["optional_nested_list"], NoneType)
    assert type_exists_at_path_any(results, ["optional_nested_list", "*"], list)
    assert type_exists_at_path_any(results, ["optional_nested_list", "*", "*"], list)
    assert type_exists_at_path_any(results, ["optional_nested_list", "*", "*", "*"], int)


def test_tuple_types() -> None:
    class Model(BaseModel):
        tii: Tuple[int, int]

    results = list(ModelFactory.create_factory(Model).coverage())
    assert type_exists_at_path_any(results, ["tii"], tuple)
    assert type_exists_at_path_any(results, ["tii", 0], int)
    assert type_exists_at_path_any(results, ["tii", 1], int)


def test_hetero_tuple_types() -> None:
    class Model(BaseModel):
        tis: Tuple[int, str]

    results = list(ModelFactory.create_factory(Model).coverage())
    assert type_exists_at_path_any(results, ["tis"], tuple)
    assert type_exists_at_path_any(results, ["tis", 0], int)
    assert type_exists_at_path_any(results, ["tis", 1], str)


def test_optional_list_uuid() -> None:
    class Model(BaseModel):
        maybe_uuids: Optional[List[UUID]]

    results = list(ModelFactory.create_factory(Model).coverage())
    assert type_exists_at_path_any(results, ["maybe_uuids"], list)
    assert type_exists_at_path_any(results, ["maybe_uuids", "*"], UUID)
    assert type_exists_at_path_any(results, ["maybe_uuids"], NoneType)


def test_optional_set_uuid() -> None:
    class Model(BaseModel):
        maybe_uuids: Optional[Set[UUID]]

    results = list(ModelFactory.create_factory(Model).coverage())
    assert type_exists_at_path_any(results, ["maybe_uuids"], set)
    assert type_exists_at_path_any(results, ["maybe_uuids", "*"], UUID)
    assert type_exists_at_path_any(results, ["maybe_uuids"], NoneType)


@pytest.mark.skipif(
    IS_PYDANTIC_V1,
    reason="This should be possible but more work needs to be done",
)
def test_optional_mixed_collecions() -> None:
    class Model(BaseModel):
        maybe_uuids: Optional[Union[Set[UUID], List[UUID]]]

    results = list(ModelFactory.create_factory(Model).coverage())
    assert type_exists_at_path_any(results, ["maybe_uuids"], set)
    assert type_exists_at_path_any(results, ["maybe_uuids"], list)
    assert type_exists_at_path_any(results, ["maybe_uuids", "*"], UUID)
    assert type_exists_at_path_any(results, ["maybe_uuids"], NoneType)
