from collections.abc import Iterable, Iterator
from typing import Generic, TypeVar

from sqlalchemy.orm.collections import collection

T = TypeVar("T")


class ListLike(Generic[T]):
    __emulates__ = list

    def __init__(self) -> None:
        self.data: list[T] = []

    def append(self, item: T) -> None:
        self.data.append(item)

    def remove(self, item: T) -> None:
        self.data.remove(item)

    def extend(self, items: Iterable[T]) -> None:
        self.data.extend(items)

    def __iter__(self) -> Iterator[T]:
        return iter(self.data)


class SetLike(Generic[T]):
    __emulates__ = set

    def __init__(self) -> None:
        self.data: set[T] = set()

    @collection.appender  # type: ignore[misc]
    def append(self, item: T) -> None:
        self.data.add(item)

    def remove(self, item: T) -> None:
        self.data.remove(item)

    def __iter__(self) -> Iterator[T]:
        return iter(self.data)
