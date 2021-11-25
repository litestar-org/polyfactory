from typing import Callable, Dict, List, Optional, TypeVar

from pydantic import BaseModel
from typing_extensions import Protocol


class DataclassProtocol(Protocol):
    def __init__(self, **kwargs):  # pylint: disable=super-init-not-called
        ...  # pragma: no cover

    __dataclass_fields__: Dict
    __dataclass_params__: Dict
    __post_init__: Optional[Callable]


T = TypeVar("T", BaseModel, DataclassProtocol)


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
