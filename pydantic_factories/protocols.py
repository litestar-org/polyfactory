# pylint: disable=unnecessary-ellipsis
from typing import Any, ClassVar, Dict, List, TypeVar, Union

from pydantic import BaseModel
from typing_extensions import Protocol


# According to https://github.com/python/cpython/blob/main/Lib/dataclasses.py#L1213
# having __dataclass_fields__ is enough to identity a dataclass.
class DataclassProtocol(Protocol):
    __dataclass_fields__: ClassVar[Dict[str, Any]]


T = TypeVar("T", bound=Union[BaseModel, DataclassProtocol])


class SyncPersistenceProtocol(Protocol[T]):
    def save(self, data: T) -> T:
        """Persist a single instance synchronously."""
        ...

    def save_many(self, data: List[T]) -> List[T]:
        """Persist multiple instances synchronously."""
        ...


class AsyncPersistenceProtocol(Protocol[T]):
    async def save(self, data: T) -> T:
        """Persist a single instance asynchronously."""
        ...

    async def save_many(self, data: List[T]) -> List[T]:
        """Persist multiple instances asynchronously."""
        ...
