from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Optional, TypeVar, Union

import pytest

from pydantic import BaseModel, Field
from pydantic import __version__ as pydantic_version

from polyfactory.factories.dataclass_factory import DataclassFactory
from polyfactory.factories.pydantic_factory import ModelFactory


class _Sentinel: ...


@dataclass
class Node:
    value: int
    union_child: Union[Node, int]  # noqa: UP007
    list_child: List[Node]  # noqa: UP006
    optional_child: Optional[Node]  # noqa: UP007
    child: Node = field(default=_Sentinel)  # type: ignore[assignment]

    def __post_init__(self) -> None:
        # Emulate recursive models set by external init, e.g. ORM relationships
        if self.child is _Sentinel:  # type: ignore[comparison-overlap]
            self.child = self


def test_recursive_model() -> None:
    factory = DataclassFactory.create_factory(Node)

    result = factory.build()
    assert result.child is result, "Default is not used"
    assert isinstance(result.union_child, int)
    assert result.optional_child is None
    assert result.list_child == []

    assert factory.build(child={"child": None}).child.child is None


class PydanticNode(BaseModel):
    value: int
    union_child: Union[PydanticNode, int]  # noqa: UP007
    list_child: List[PydanticNode]  # noqa: UP006
    optional_union_child: Union[PydanticNode, None]  # noqa: UP007
    optional_child: Optional[PydanticNode]  # noqa: UP007
    child: PydanticNode = Field(default=_Sentinel)  # type: ignore[assignment]
    recursive_key: Dict[PydanticNode, Any]  # noqa: UP006
    recursive_value: Dict[str, PydanticNode]  # noqa: UP006


@pytest.mark.parametrize("factory_use_construct", (True, False))
def test_recursive_pydantic_models(factory_use_construct: bool) -> None:
    factory = ModelFactory.create_factory(PydanticNode)

    result = factory.build(factory_use_construct)
    assert result.child is _Sentinel, "Default is not used"  # type: ignore[comparison-overlap]
    assert isinstance(result.union_child, int)
    assert result.optional_union_child is None
    assert result.optional_child is None
    assert result.list_child == []
    assert result.recursive_key == {}
    assert result.recursive_value == {}


@dataclass
class Author:
    name: str
    books: List[Book]  # noqa: UP006


_DEFAULT_AUTHOR = Author(name="default", books=[])


@dataclass
class Book:
    name: str
    author: Author = field(default_factory=lambda: _DEFAULT_AUTHOR)


def test_recursive_list_model() -> None:
    factory = DataclassFactory.create_factory(Author)
    assert factory.build().books[0].author is _DEFAULT_AUTHOR
    assert factory.build(books=[]).books == []

    book_factory = DataclassFactory.create_factory(Book)
    assert book_factory.build().author.books == []
    assert book_factory.build(author=None).author is None


@pytest.mark.skipif(pydantic_version.startswith("1"), reason="Pydantic v2+ is required for JsonValue")
def test_recursive_type_annotation() -> None:
    from pydantic import JsonValue

    class RecursiveTypeModel(BaseModel):
        json_value: JsonValue

    factory = ModelFactory.create_factory(RecursiveTypeModel)
    results = factory.batch(50)

    valid_types = {int, str, bool, float, dict, list, type(None)}

    assert _get_types(result.json_value for result in results) == valid_types
    assert _get_types(result.json_value for result in factory.coverage()) == valid_types


RecursiveType = Union[List["RecursiveType"], int]


def test_recursive_model_with_forward_ref() -> None:
    @dataclass
    class RecursiveTypeModel:
        json_value: RecursiveType

    factory = DataclassFactory.create_factory(
        RecursiveTypeModel,
        __forward_references__={"RecursiveType": int},
    )
    results = factory.batch(50)

    valid_types = {int, list}

    assert _get_types(result.json_value for result in results) == valid_types
    assert _get_types(result.json_value for result in factory.coverage()) == valid_types


_T = TypeVar("_T")


def _get_types(items: Iterable[_T]) -> set[type[_T]]:
    return {type(item) for item in items}
