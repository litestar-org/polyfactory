from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from polyfactory.factories.dataclass_factory import DataclassFactory


@dataclass
class Node:
    a: int
    child: Optional[Node]  # noqa: UP007


def test_recusive_model() -> None:
    factory = DataclassFactory.create_factory(Node)
    assert factory.build().child is None
    assert factory.build(child={"child": None}).child.child is None  # type: ignore[union-attr]


@dataclass
class Author:
    name: str
    books: List[Book]  # noqa: UP006


@dataclass
class Book:
    name: str
    author: Author


def test_recusive_list_model() -> None:
    factory = DataclassFactory.create_factory(Author)
    assert factory.build().books[0].author is None
    assert factory.build(books=[]).books == []

    book_factory = DataclassFactory.create_factory(Book)
    assert book_factory.build().author.books == []
    assert book_factory.build(author=None).author is None
