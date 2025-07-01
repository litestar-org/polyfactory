from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Union

import pytest

from pydantic import BaseModel, Field

from polyfactory.factories.dataclass_factory import DataclassFactory
from polyfactory.factories.pydantic_factory import ModelFactory


class _Sentinel: ...


@dataclass
class Node:
    value: int
    union_child: Union[Node, int]  # noqa: UP007
    list_child: list[Node]
    optional_child: Union[Node, None]  # noqa: UP007
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
    list_child: list[PydanticNode]
    optional_union_child: Union[PydanticNode, None]  # noqa: UP007
    optional_child: Union[PydanticNode, None]  # noqa: UP007
    child: PydanticNode = Field(default=_Sentinel)  # type: ignore[assignment]
    recursive_key: dict[PydanticNode, Any]
    recursive_value: dict[str, PydanticNode]


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
    books: list[Book]


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
