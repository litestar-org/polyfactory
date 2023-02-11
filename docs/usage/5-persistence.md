# Persistence

`ModelFactory` has four persistence methods:

- `.create_sync(**kwargs)` - builds and persists a single instance of the factory's model synchronously
- `.create_batch_sync(size: int, **kwargs)` - builds and persists a list of size n instances synchronously
- `.create_async(**kwargs)` - builds and persists a single instance of the factory's model asynchronously
- `.create_batch_async(size: int, **kwargs)` - builds and persists a list of size n instances asynchronously

To use these methods, you must first specify a sync and/or async persistence handlers for the factory:

```python
from polyfactory.factories.pydantic_factory import ModelFactory
from typing import TypeVar, List

from pydantic import BaseModel
from polyfactory import SyncPersistenceProtocol, AsyncPersistenceProtocol

T = TypeVar("T", bound=BaseModel)


class SyncPersistenceHandler(SyncPersistenceProtocol[T]):
    def save(self, data: T) -> T:
        ...  # do stuff

    def save_many(self, data: List[T]) -> List[T]:
        ...  # do stuff


class AsyncPersistenceHandler(AsyncPersistenceProtocol[T]):
    async def save(self, data: T) -> T:
        ...  # do stuff

    async def save_many(self, data: List[T]) -> List[T]:
        ...  # do stuff


class PersonFactory(ModelFactory):
    __sync_persistence__ = SyncPersistenceHandler
    __async_persistence__ = AsyncPersistenceHandler
    ...
```

Or create your own base factory and reuse it in your various factories:

```python
from polyfactory.factories.pydantic_factory import ModelFactory
from typing import TypeVar, List

from pydantic import BaseModel
from polyfactory import SyncPersistenceProtocol, AsyncPersistenceProtocol

T = TypeVar("T", bound=BaseModel)


class SyncPersistenceHandler(SyncPersistenceProtocol[T]):
    def save(self, data: T) -> T:
        ...  # do stuff

    def save_many(self, data: List[T]) -> List[T]:
        ...  # do stuff


class AsyncPersistenceHandler(AsyncPersistenceProtocol[T]):
    async def save(self, data: T) -> T:
        ...  # do stuff

    async def save_many(self, data: List[T]) -> List[T]:
        ...  # do stuff


class BaseModelFactory(ModelFactory):
    __sync_persistence__ = SyncPersistenceHandler
    __async_persistence__ = AsyncPersistenceHandler


class PersonFactory(BaseModelFactory):
    ...
```

With the persistence handlers in place, you can now use all persistence methods. Please note - you do not need to define
any or both persistence handlers. If you will only use sync or async persistence, you only need to define the respective
handler to use these methods.

## Create Factory Method

If you prefer to create a factory imperatively, you can do so using the `ModelFactory.create_factory` method. This method receives the following arguments:

- model - the model for the factory.
- base - an optional base factory class. Defaults to the factory class on which the method is called.
- kwargs - a dictionary of arguments correlating to the class vars accepted by ModelFactory, e.g. **faker**.

You could also override the child factory's `__model__` attribute to specify the model to use and the default kwargs as shown as the BuildPet class as shown below:

```python
from datetime import date, datetime
from enum import Enum
from pydantic import BaseModel, UUID4
from typing import Any, Dict, List, TypeVar, Union, Generic, Optional
from polyfactory.factories.pydantic_factory import ModelFactory


class Species(str, Enum):
    CAT = "Cat"
    DOG = "Dog"


class PetBase(BaseModel):
    name: str
    species: Species


class Pet(PetBase):
    id: UUID4


class PetCreate(PetBase):
    pass


class PetUpdate(PetBase):
    pass


class PersonBase(BaseModel):
    name: str
    hobbies: List[str]
    age: Union[float, int]
    birthday: Union[datetime, date]
    pets: List[Pet]
    assets: List[Dict[str, Dict[str, Any]]]


class PersonCreate(PersonBase):
    pass


class Person(PersonBase):
    id: UUID4


class PersonUpdate(PersonBase):
    pass


def test_factory():
    class PersonFactory(ModelFactory):
        __model__ = Person

    person = PersonFactory.build()

    assert person.pets != []


ModelType = TypeVar("ModelType", bound=BaseModel)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class BUILDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(
            self,
            model: ModelType = None,
            create_schema: Optional[CreateSchemaType] = None,
            update_schema: Optional[UpdateSchemaType] = None,
    ):
        self.model = model
        self.create_model = create_schema
        self.update_model = update_schema

    def build_object(self) -> ModelType:
        object_Factory = ModelFactory.create_factory(self.model)
        return object_Factory.build()

    def build_create_object(self) -> CreateSchemaType:
        object_Factory = ModelFactory.create_factory(self.create_model)
        return object_Factory.build()

    def build_update_object(self) -> UpdateSchemaType:
        object_Factory = ModelFactory.create_factory(self.update_model)
        return object_Factory.build()


class BUILDPet(BUILDBase[Pet, PetCreate, PetUpdate]):
    def build_object(self) -> Pet:
        object_Factory = ModelFactory.create_factory(self.model, name="Fido")
        return object_Factory.build()

    def build_create_object(self) -> PetCreate:
        object_Factory = ModelFactory.create_factory(self.create_model, name="Rover")
        return object_Factory.build()

    def build_update_object(self) -> PetUpdate:
        object_Factory = ModelFactory.create_factory(self.update_model, name="Spot")
        return object_Factory.build()


def test_factory_create():
    person_factory = BUILDBase(Person, PersonCreate, PersonUpdate)

    pet_factory = BUILDPet(Pet, PetCreate, PetUpdate)

    create_person = person_factory.build_create_object()
    update_person = person_factory.build_update_object()

    pet = pet_factory.build_object()
    create_pet = pet_factory.build_create_object()
    update_pet = pet_factory.build_update_object()

    assert create_person is not None
    assert update_person is not None

    assert pet.name == "Fido"
    assert create_pet.name == "Rover"
    assert update_pet.name == "Spot"
```
