![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pydantic-factories)
[![Coverage](https://sonarcloud.io/api/project_badges/measure?project=Goldziher_pydantic-factories&metric=coverage)](https://sonarcloud.io/summary/new_code?id=Goldziher_pydantic-factories)
[![Maintainability Rating](https://sonarcloud.io/api/project_badges/measure?project=Goldziher_pydantic-factories&metric=sqale_rating)](https://sonarcloud.io/summary/new_code?id=Goldziher_pydantic-factories)
[![Reliability Rating](https://sonarcloud.io/api/project_badges/measure?project=Goldziher_pydantic-factories&metric=reliability_rating)](https://sonarcloud.io/summary/new_code?id=Goldziher_pydantic-factories)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=Goldziher_pydantic-factories&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=Goldziher_pydantic-factories)

# Overview

**pydantic-factories** is a library for generating testing data
from [pydantic](https://github.com/samuelcolvin/pydantic) based models. This library can be used with pydantic as well
as any other library that uses pydantic as a foundation, such as [SQLModel](https://github.com/tiangolo/sqlmodel)
, [ormar](https://github.com/collerek/ormar)
and [Beanie](https://github.com/roman-right/beanie).

### Features

- ✅ supports both built-in and pydantic types
- ✅ supports pydantic field constraints
- ✅ supports complex field typings
- ✅ supports custom model fields

### Why This Library?

- 💯 powerful
- 💯 extensible
- 💯 simple
- 💯 rigorously tested

## Installation

Using your package manager of choice:

```sh
pip install pydantic-factories
```

OR

```sh
poetry add --dev pydantic-factories
```

OR

```sh
pipenv install --dev pydantic-factories
```

**pydantic-factories** has very few dependencies aside from _pydantic_ - [
typing-extensions](https://github.com/python/typing/blob/master/typing_extensions/README.rst) which is used for typing
support in older versions of python, and [faker](https://github.com/joke2k/faker)
and [exrex](https://github.com/asciimoo/exrex), both of which are used for generating mock data.

## Usage

```python
from datetime import date, datetime
from typing import List, Union

from pydantic import BaseModel, UUID4

from pydantic_factories import ModelFactory


class Person(BaseModel):
    id: UUID4
    name: str
    hobbies: List[str]
    age: Union[float, int]
    birthday: Union[datetime, date]


class PersonFactory(ModelFactory):
    __model__ = Person


result = PersonFactory.build()
```

That's it - with almost no work, we are able to create a mock data object fitting the `Person` class model definition.

This is possible because of the typing information available on the pydantic model and model-fields, which are used as a
source of truth for data generation.

The factory parses the information stored in the pydantic model and generates a dictionary of kwargs that are passed to
the `Person` class's init method.

### Build Methods

`ModelFactory` exposes two build methods:

- `.build(**kwargs)` - builds a single instance of the factory's model
- `.batch(size: int, **kwargs)` - build a list of size n instances

```python
result = PersonFactory.build()  # a single Person instance

result = PersonFactory.batch(size=5)  # list[Person, Person, Person, Person, Person]
```

Any `kwargs` you pass to `.build`, `.batch` or any of the [persistence methods](#persistence), will take precedence over
whatever defaults are defined on the factory class.

### Nested Models and Complex Typings

The automatic generation of mock data works for all types supported by pydantic, as well as nested classes that derive
from `BaseModel` (including for 3rd party libraries) and complex custom typings. Lets look at another example:

```python
from datetime import date, datetime
from enum import Enum
from pydantic import BaseModel, UUID4
from typing import Any, Dict, List, Union

from pydantic_factories import ModelFactory


class Species(str, Enum):
    CAT = "Cat"
    DOG = "Dog"
    PIG = "Pig"
    MONKEY = "Monkey"


class Pet(BaseModel):
    name: str
    sound: str
    species: Species


class Person(BaseModel):
    id: UUID4
    name: str
    hobbies: List[str]
    age: Union[float, int]
    birthday: Union[datetime, date]
    pets: List[Pet]
    assets: List[Dict[str, Dict[str, Any]]]


class PersonFactory(ModelFactory):
    __model__ = Person


result = PersonFactory.build()
```

This example will also work out of the box: although no factory was defined for the Pet class that's not a problem - a
factory will be dynamically generated for it on the fly.

The complex typing under the `assets` attribute is a bit more tricky, but the factory will generate a python object
fitting this signature. Hence passing validation.

**Please note**: the one thing factories cannot handle is self referencing models. In this case you will need to handle
the particular field by setting defaults for it.

### Factory Configuration

Configuration of `ModelFactory` is done using class variables:

- **\_\_model\_\_**: a _required_ variable specifying the model for the factory. It accepts any class that extends _
  pydantic's_ `BaseModel` including classes from other libraries. If this variable is not set,
  a `ConfigurationException` will be raised.

- **\_\_faker\_\_**: an _optional_ variable specifying a user configured instance of faker. If this variable is not set,
  the factory will default to using vanilla `faker`.

- **\_\_sync_persistence\_\_**: an _optional_ variable specifying the handler for synchronously persisting data. If this
  is variable is not set, the `.create_sync` and `.create_batch_sync` methods of the factory cannot be used.
  See: [persistence methods](#persistence)

- **\_\_async_persistence\_\_**: an _optional_ variable specifying the handler for asynchronously persisting data. If
  this is variable is not set, the `.create_async` and `.create_batch_async` methods of the factory cannot be used.
  See: [persistence methods](#persistence)

```python
from faker import Faker
from pydantic_factories import ModelFactory

from app.models import Person
from .persistence import AsyncPersistenceHandler, SyncPersistenceHandler

Faker.seed(5)
my_faker = Faker("en-EN")


class PersonFactory(ModelFactory):
    __model__ = Person
    __faker__ = my_faker
    __sync_persistence__ = SyncPersistenceHandler
    __async_persistence__ = AsyncPersistenceHandler
    ...
```

### Defining Factory Attributes

The factory api is designed to be as semantic and simple as possible, lets look at several different examples assuming
we have the following models:

```python
from datetime import date, datetime
from enum import Enum
from pydantic import BaseModel, UUID4
from typing import Any, Dict, List, Union

from pydantic_factories import ModelFactory


class Species(str, Enum):
    CAT = "Cat"
    DOG = "Dog"


class Pet(BaseModel):
    name: str
    species: Species


class Person(BaseModel):
    id: UUID4
    name: str
    hobbies: List[str]
    age: Union[float, int]
    birthday: Union[datetime, date]
    pets: List[Pet]
    assets: List[Dict[str, Dict[str, Any]]]
```

One way of defining defaults is to use hardcoded values:

```python
pet = Pet(name="Roxy", sound="woof woof", species=Species.DOG)


class PersonFactory(ModelFactory):
    __model__ = Person
    pets = [pet]

```

In this case when we call `PersonFactory.build()` the result will be randomly generated, except the pets list, which
will be the hardcoded default we defined.

#### Use (field)

This though is often not desirable. We could instead, define a factory for `Pet` where we restrict the choices to a
range we like. For example:

```python
from enum import Enum
from pydantic_factories.fields import Use
from random import choice


class Species(str, Enum):
    CAT = "Cat"
    DOG = "Dog"


class PetFactory(ModelFactory):
    __model__ = Pet

    name = Use(choice, ["Ralph", "Roxy"])
    species = Use(choice, list(Species))


class PersonFactory(ModelFactory).


__model__ = Person

pets = Use(PetFactory.batch, size=2)
```

The signature for use is: `cb: Callable, *args, **defaults`, it can receive any sync callable and whatever arguments and
keyword arguments it should receive. In the above example, we used the `choice` function from the standard library, and
the batch method of `PetFactory`.

You do not need to use the `Use` field, **you can place callables (including classes) as values for a factory's
attribute**, and these will be invoked at build-time. Thus you could for example write the above `PetFactory` like so:

```python
class PetFactory(ModelFactory):
    __model__ = Pet

    name = lambda: choice(["Ralph", "Roxy"])
    species = lambda: choice(list(Species)
```

`Use` is merely a semantic abstraction that makes the factory cleaner and simpler to understand.

#### Ignore (field)

There are another two special fields you can use in your factory `Ignore` and `Require`, lets look at an example
of `Ignore` first:

```python
from odmantic import EmbeddedModel, Model

T = TypeVar("T", Model, EmbeddedModel)


class OdmanticModelFactory(ModelFactory[T]):
    id = Ignore()

```

This is basically the extension included in `pydantic-factories` for the
library [odmantic](https://github.com/art049/odmantic), which is a pydantic based mongo ODM. For odmantic models,
the `id` attribute should not be set by the factory, but rather handled by the odmantic logic itself.

When you ignore an attribute using `Ignore`, it will be completely ignored by the factory - that is, it will not be set
as a kwarg passed to pydantic at all.

#### Require (field)

`Require` in turn specifies that a particular attribute is a **required kwarg**, that is, if a kwarg with a value for
this particular attribute is not passed when calling `factory.build()`, an exception will be raised.

What is the use case for this? For example, lets say we have a document called `Article` which we store in some DB and
is represented using a non-pydantic model, say, an `elastic-dsl` document. We then need to store in our pydantic object
a reference to an id for this article. This value should not be some mock value, but must rather be an actual id passed
to the factory. Thus we can define this attribute as required:

```python
from pydantic import BaseModel
from pydantic_factories import ModelFactory, Require
from uuid import UUID


class ArticleProxy(BaseModel):
    article_id: UUID
    ...


class ArticleProxyFactory():
    __model__ = ArticleProxy

    article_id = Require()
```

If we call `factory.build()` without passing a value for article_id, an error will be raised.

### Persistence

`ModelFactory` has four persistence methods:

- `.create_sync(**kwargs)` - builds and persists a single instance of the factory's model synchronously
- `.create_batch_sync(size: int, **kwargs)` - builds and persists a list of size n instances synchronously
- `.create_async(**kwargs)` - builds and persists a single instance of the factory's model asynchronously
- `.create_batch_async(size: int, **kwargs)` - builds and persists a list of size n instances asynchronously

To use these methods, you must first specify a sync and/or async persistence handlers for the factory:

```python
# persistence.py
from typing import TypeVar, List

from pydantic import BaseModel
from pydantic_factories import SyncPersistenceProtocol

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

```

You can then specify one or both of these handlers in your factory:

```python
from pydantic_factories import ModelFactory

from app.models import Person
from .persistence import AsyncPersistenceHandler, SyncPersistenceHandler


class PersonFactory(ModelFactory):
    __model__ = Person
    __sync_persistence__ = SyncPersistenceHandler
    __async_persistence__ = AsyncPersistenceHandler
```

Or create your own base factory and reuse it in your various factories:

```python
from pydantic_factories import ModelFactory

from app.models import Person
from .persistence import AsyncPersistenceHandler, SyncPersistenceHandler


class BaseModelFactory(ModelFactory):
    __sync_persistence__ = SyncPersistenceHandler
    __async_persistence__ = AsyncPersistenceHandler


class PersonFactory(BaseModelFactory):
    __model__ = Person
```

With the persistence handlers in place, you can now use all persistence methods. Please note - you do not need to define
any or both persistence handlers. If you will only use sync or async persistence, you only need to define the respective
handler to use these methods.

## Extensions and Third Party Libraries

Any class that is derived from pydantic's `BaseModel` can be used as the `__model__` of a factory. For most 3rd party
libraries, e.g. [SQLModel](https://sqlmodel.tiangolo.com/) or [Ormar](https://collerek.github.io/ormar/), this library
will work as is out of the box.

Currently, this library also includes extensions for two ODM libraries - odmatic and Beanie.
