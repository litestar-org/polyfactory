# pylint: disable=unnecessary-ellipsis
from dataclasses import Field
from typing import (
    TYPE_CHECKING,
    Dict,
    List,
    Optional,
    Protocol,
    TypeVar,
    runtime_checkable,
)

T = TypeVar("T")

if TYPE_CHECKING:
    from random import Random


class NumberGeneratorProtocol(Protocol[T]):
    def __call__(self, random: "Random", minimum: Optional[T] = None, maximum: Optional[T] = None) -> T:
        ...


@runtime_checkable
class DataclassProtocol(Protocol):
    __dataclass_fields__: Dict[str, Field]


@runtime_checkable
class SyncPersistenceProtocol(Protocol[T]):
    def save(self, data: T) -> T:
        """Persist a single instance synchronously."""
        ...

    def save_many(self, data: List[T]) -> List[T]:
        """Persist multiple instances synchronously."""
        ...


@runtime_checkable
class AsyncPersistenceProtocol(Protocol[T]):
    async def save(self, data: T) -> T:
        """Persist a single instance asynchronously."""
        ...

    async def save_many(self, data: List[T]) -> List[T]:
        """Persist multiple instances asynchronously."""
        ...
