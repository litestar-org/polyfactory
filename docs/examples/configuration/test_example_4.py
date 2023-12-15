from asyncio import sleep
from dataclasses import dataclass
from typing import Dict, List
from uuid import UUID

from polyfactory import AsyncPersistenceProtocol, SyncPersistenceProtocol
from polyfactory.factories import DataclassFactory


@dataclass
class Person:
    id: UUID
    name: str


# we will use a dictionary to persist values for the example
mock_db: Dict[UUID, Person] = {}


class SyncPersistenceHandler(SyncPersistenceProtocol[Person]):
    def save(self, data: Person) -> Person:
        # do stuff here to persist the value, such as use an ORM or ODM, cache in redis etc.
        # in our case we simply save it in the dictionary.
        mock_db[data.id] = data
        return data

    def save_many(self, data: List[Person]) -> List[Person]:
        # same as for save, here we should store the list in persistence.
        # in this case, we use the same dictionary.
        for person in data:
            mock_db[person.id] = person
        return data


class AsyncPersistenceHandler(AsyncPersistenceProtocol[Person]):
    async def save(self, data: Person) -> Person:
        # do stuff here to persist the value using an async method, such as an async ORM or ODM.
        # in our case we simply save it in the dictionary and add a minimal sleep to mock async.
        mock_db[data.id] = data
        await sleep(0.0001)
        return data

    async def save_many(self, data: List[Person]) -> List[Person]:
        # same as for the async save, here we should store the list in persistence using async logic.
        # we again store in dict, and mock async using sleep.
        for person in data:
            mock_db[person.id] = person
        await sleep(0.0001)
        return data


class PersonFactory(DataclassFactory[Person]):
    __sync_persistence__ = SyncPersistenceHandler
    __async_persistence__ = AsyncPersistenceHandler


def test_sync_persistence_build() -> None:
    person_instance = PersonFactory.create_sync()
    assert mock_db[person_instance.id] is person_instance


def test_sync_persistence_batch() -> None:
    person_batch = PersonFactory.create_batch_sync(10)
    for person_instance in person_batch:
        assert mock_db[person_instance.id] is person_instance


async def test_async_persistence_build() -> None:
    person_instance = await PersonFactory.create_async()
    assert mock_db[person_instance.id] is person_instance


async def test_async_persistence_batch() -> None:
    person_batch = await PersonFactory.create_batch_async(10)
    for person_instance in person_batch:
        assert mock_db[person_instance.id] is person_instance
