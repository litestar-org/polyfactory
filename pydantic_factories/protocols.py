from typing import List, TypeVar

from pydantic import BaseModel
from typing_extensions import Protocol

T = TypeVar("T", bound=BaseModel)


class SyncPersistenceProtocol(Protocol[T]):
    def save(self, data: T, *args, **kwargs) -> T:
        """Persist a single instance synchronously"""
        ...

    def save_many(self, data: List[T], *args, **kwargs) -> List[T]:
        """Persist multiple instances synchronously"""
        ...


class AsyncPersistenceProtocol(Protocol[T]):
    async def save(self, data: T, *args, **kwargs) -> T:
        """Persist a single instance asynchronously"""
        ...

    async def save_many(self, data: List[T], *args, **kwargs) -> List[T]:
        """Persist multiple instances asynchronously"""
        ...
