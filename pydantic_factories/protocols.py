from typing import List, TypeVar

from pydantic import BaseModel
from typing_extensions import Protocol

T = TypeVar("T", bound=BaseModel)


class SyncPersistenceProtocol(Protocol[T]):
    def save(self, data: T) -> T:
        """Persist a single instance synchronously"""
        ...  # pragma: no cover

    def save_many(self, data: List[T]) -> List[T]:
        """Persist multiple instances synchronously"""
        ...  # pragma: no cover


class AsyncPersistenceProtocol(Protocol[T]):
    async def save(self, data: T) -> T:
        """Persist a single instance asynchronously"""
        ...  # pragma: no cover

    async def save_many(self, data: List[T]) -> List[T]:
        """Persist multiple instances asynchronously"""
        ...  # pragma: no cover
