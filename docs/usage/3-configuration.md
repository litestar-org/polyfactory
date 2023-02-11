# Factory Configuration

Configuration of `ModelFactory` is done using class variables:

- **\_\_model\_\_**: a _required_ variable specifying the model for the factory. It accepts any class that extends _
  pydantic's_ `BaseModel` including classes from other libraries. If this variable is not set,
  a `ConfigurationException` will be raised.

- **\_\_faker\_\_**: an _optional_ variable specifying a user configured instance of faker. If this variable is not set,
  the factory will default to using vanilla `faker`.

- **\_\_sync_persistence\_\_**: an _optional_ variable specifying the handler for synchronously persisting data. If this
  is variable is not set, the `.create_sync` and `.create_batch_sync` methods of the factory cannot be used.
  See: [persistence methods](./5-persistence.md)

- **\_\_async_persistence\_\_**: an _optional_ variable specifying the handler for asynchronously persisting data. If
  this is variable is not set, the `.create_async` and `.create_batch_async` methods of the factory cannot be used.
  See: [persistence methods](./5-persistence.md)

- **\_\_allow_none_optionals\_\_**: an _optional_ variable specifying whether the factory should randomly set None
  values for optional fields, or always set a value for them. This is `True` by default.

```python
from faker import Faker
from polyfactory.factories.pydantic_factory import ModelFactory

from app.models import Person
from .persistence import AsyncPersistenceHandler, SyncPersistenceHandler

Faker.seed(5)
my_faker = Faker("en-EN")


class PersonFactory(ModelFactory):
    __model__ = Person
    __faker__ = my_faker
    __sync_persistence__ = SyncPersistenceHandler
    __async_persistence__ = AsyncPersistenceHandler
    __allow_none_optionals__ = False
    ...
```

## Generating deterministic objects

In order to generate deterministic data, use `ModelFactory.seed_random` method. This will pass the seed value to both
Faker and random method calls, guaranteeing data to be the same in between the calls. Especially useful for testing.
