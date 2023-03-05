# pylint: disable=unnecessary-ellipsis
from typing import List, Protocol, TypeVar, runtime_checkable

T = TypeVar("T")


@runtime_checkable
class SyncPersistenceProtocol(Protocol[T]):
    """Protocol for sync persistence"""

    def save(self, data: T) -> T:
        """Persist a single instance synchronously.

        :param data: A single instance to persist.
        :return: The persisted result.
        """
        ...

    def save_many(self, data: List[T]) -> List[T]:
        """Persist multiple instances synchronously.

        :param data: A sequence of instances to persist.
        :return: The persisted result
        """
        ...


@runtime_checkable
class AsyncPersistenceProtocol(Protocol[T]):
    """Protocol for async persistence"""

    async def save(self, data: T) -> T:
        """Persist a single instance asynchronously.

        :param data: A single instance to persist.
        :return: The persisted result.
        """
        ...

    async def save_many(self, data: List[T]) -> List[T]:
        """Persist multiple instances asynchronously.

        :param data: A sequence of instances to persist.
        :return: The persisted result
        """
        ...
