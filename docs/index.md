<!-- markdownlint-disable -->
<center>

![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pydantic-factories)

[![Language grade: Python](https://img.shields.io/lgtm/grade/python/g/Goldziher/pydantic-factories.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/Goldziher/pydantic-factories/context:python)
[![Total alerts](https://img.shields.io/lgtm/alerts/g/Goldziher/pydantic-factories.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/Goldziher/pydantic-factories/alerts/)
[![Coverage](https://sonarcloud.io/api/project_badges/measure?project=Goldziher_pydantic-factories&metric=coverage)](https://sonarcloud.io/summary/new_code?id=Goldziher_pydantic-factories)
[![Maintainability Rating](https://sonarcloud.io/api/project_badges/measure?project=Goldziher_pydantic-factories&metric=sqale_rating)](https://sonarcloud.io/summary/new_code?id=Goldziher_pydantic-factories)
[![Reliability Rating](https://sonarcloud.io/api/project_badges/measure?project=Goldziher_pydantic-factories&metric=reliability_rating)](https://sonarcloud.io/summary/new_code?id=Goldziher_pydantic-factories)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=Goldziher_pydantic-factories&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=Goldziher_pydantic-factories)

[![Discord](https://img.shields.io/discord/919193495116337154?color=blue&label=chat%20on%20discord&logo=discord)](https://discord.gg/X3FJqy8d2j)

</center>
<!-- markdownlint-restore -->

# Pydantic-Factories

This library offers powerful mock data generation capabilities for [pydantic](https://github.com/samuelcolvin/pydantic)
based models and `dataclasses`. It can also be used with other libraries that use pydantic as a foundation, for
example [SQLModel](https://github.com/tiangolo/sqlmodel) and [Beanie](https://github.com/roman-right/beanie).

## Table of Contents

<!-- TOC start -->

- [Pydantic-Factories](#pydantic-factories)
  - [Table of Contents](#table-of-contents)
    - [Example](#example)
    - [Features](#features)
    - [Why This Library?](#why-this-library)
  - [Installation](#installation)
  - [Usage](#usage)
    - [Build Methods](#build-methods)
    - [Nested Models and Complex types](#nested-models-and-complex-types)
    - [Models and Dataclasses](#models-and-dataclasses)
      - [Note Regarding Nested Optional Types in Dataclasses](#note-regarding-nested-optional-types-in-dataclasses)
    - [Factory Configuration](#factory-configuration)
      - [Generating deterministic objects](#generating-deterministic-objects)
    - [Defining Factory Attributes](#defining-factory-attributes)
      - [Use (field)](#use-field)
      - [PostGenerated (field)](#postgenerated-field)
      - [Ignore (field)](#ignore-field)
      - [Require (field)](#require-field)
    - [Persistence](#persistence)
  - [Create Factory Method](#create-factory-method)
  - [Extensions and Third Party Libraries](#extensions-and-third-party-libraries)
    - [ODMantic](#odmantic)
    - [Beanie](#beanie)
    - [Ormar](#ormar)
    - [Adding Factory Values](#adding-factory-values)
  - [Plugins](#plugins)
    - [Pytest](#pytest)
  - [Partial parameters random generation](#partial-parameters-random-generation)
  - [Frequently Asked Questions (FAQs)](#frequently-asked-questions-faqs)
  <!-- TOC end -->

### Example

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
the `Person` class' init method.

### Features

- ✅ supports both built-in and pydantic types
- ✅ supports pydantic field constraints
- ✅ supports complex field types
- ✅ supports custom model fields

### Why This Library?

- 💯 powerful
- 💯 extensible
- 💯 simple
- 💯 rigorously tested

See [Frequently Asked Questions (FAQs)](#frequently-asked-questions-faqs) for more information.

## Installation

```sh
pip install pydantic-factories
```

**pydantic-factories** has very few dependencies aside from _pydantic_ - [
typing-extensions](https://github.com/python/typing/blob/master/typing_extensions/README.rst) which is used for typing
support in older versions of python, as well as [faker](https://github.com/joke2k/faker)
and [xeger](https://github.com/crdoconnor/xeger), both of which are used for generating mock data.

## Usage

### Build Methods

The `ModelFactory` class exposes two build methods:

- `.build(**kwargs)` - builds a single instance of the factory's model
- `.batch(size: int, **kwargs)` - build a list of size n instances

```python
from pydantic import BaseModel

from pydantic_factories import ModelFactory


class Person(BaseModel):
    ...


class PersonFactory(ModelFactory):
    __model__ = Person


single_result = PersonFactory.build()  # a single Person instance

batch_result = PersonFactory.batch(
    size=5
)  # list[Person, Person, Person, Person, Person]
```

Any `kwargs` you pass to `.build`, `.batch` or any of the [persistence methods](#persistence), will take precedence over
whatever defaults are defined on the factory class itself.

By default, when building a pydantic class, kwargs are validated, to avoid input validation you can use the `factory_use_construct` param.

```python
from pydantic import BaseModel

from pydantic_factories import ModelFactory


class Person(BaseModel):
    ...


class PersonFactory(ModelFactory):
    __model__ = Person


PersonFactory.build(id=5)  # Raises a validation error

result = PersonFactory.build(
    factory_use_construct=True, id=5
)  # Build a Person with invalid id
```

### Nested Models and Complex types

The automatic generation of mock data works for all types supported by pydantic, as well as nested classes that derive
from `BaseModel` (including for 3rd party libraries) and complex types. Let's look at another example:

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

This example will also work out of the box although no factory was defined for the Pet class, that's not a problem - a
factory will be dynamically generated for it on the fly.

The complex typing under the `assets` attribute is a bit more tricky, but the factory will generate a python object
fitting this signature, therefore passing validation.

**Please note**: the one thing factories cannot handle is self referencing models, because this can lead to recursion
errors. In this case you will need to handle the particular field by setting defaults for it.

### Models and Dataclasses

This library works with any class that inherits the pydantic `BaseModel` class, including `GenericModel` and classes
from 3rd party libraries, and also with dataclasses - both those from the python standard library and pydantic's
dataclasses. In fact, you can use them interchangeably as you like:

```python
import dataclasses
from typing import Dict, List

import pydantic
from pydantic_factories import ModelFactory


@pydantic.dataclasses.dataclass
class MyPydanticDataClass:
    name: str


class MyFirstModel(pydantic.BaseModel):
    dataclass: MyPydanticDataClass


@dataclasses.dataclass()
class MyPythonDataClass:
    id: str
    complex_type: Dict[str, Dict[int, List[MyFirstModel]]]


class MySecondModel(pydantic.BaseModel):
    dataclasses: List[MyPythonDataClass]


class MyFactory(ModelFactory):
    __model__ = MySecondModel


result = MyFactory.build()
```

The above example will build correctly.

#### Note Regarding Nested Optional Types in Dataclasses

When generating mock values for fields typed as `Optional`, if the factory is defined
with `__allow_none_optionals__ = True`, the field value will be either a value or None - depending on a random decision.
This works even when the `Optional` typing is deeply nested, except for dataclasses - typing is only shallowly evaluated
for dataclasses, and as such they are always assumed to require a value. If you wish to have a None value, in this
particular case, you should do so manually by configured a `Use` callback for the particular field.

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

- **\_\_allow_none_optionals\_\_**: an _optional_ variable specifying whether the factory should randomly set None
  values for optional fields, or always set a value for them. This is `True` by default.

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
    __allow_none_optionals__ = False
    ...
```

#### Generating deterministic objects

In order to generate deterministic data, use `ModelFactory.seed_random` method. This will pass the seed value to both
Faker and random method calls, guaranteeing data to be the same in between the calls. Especially useful for testing.

### Defining Factory Attributes

The factory api is designed to be as semantic and simple as possible, lets look at several examples that assume we have
the following models:

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
from datetime import date, datetime
from pydantic import BaseModel, UUID4
from typing import Any, Dict, List, Union
from enum import Enum
from pydantic_factories import ModelFactory, Use
from random import choice


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


class PetFactory(ModelFactory):
    __model__ = Pet

    name = Use(choice, ["Ralph", "Roxy"])
    species = Use(choice, list(Species))


class PersonFactory(ModelFactory):
    __model__ = Person

    pets = Use(PetFactory.batch, size=2)
```

The signature for use is: `cb: Callable, *args, **defaults`, it can receive any sync callable. In the above example, we
used the `choice` function from the standard library's `random` package, and the batch method of `PetFactory`.

You do not need to use the `Use` field, **you can place callables (including classes) as values for a factory's
attribute** directly, and these will be invoked at build-time. Thus, you could for example re-write the
above `PetFactory` like so:

```python
from enum import Enum
from pydantic import BaseModel
from random import choice
from pydantic_factories import ModelFactory


class Species(str, Enum):
    CAT = "Cat"
    DOG = "Dog"


class Pet(BaseModel):
    name: str
    species: Species


class PetFactory(ModelFactory):
    __model__ = Pet

    name = lambda: choice(["Ralph", "Roxy"])  # noqa: E731
    species = lambda: choice(list(Species))  # noqa: E731
```

`Use` is merely a semantic abstraction that makes the factory cleaner and simpler to understand.

#### PostGenerated (field)

It allows for post generating fields based on already generated values of other (non post generated) fields. In most
cases this pattern is best avoided, but for the few valid cases the `PostGenerated` helper is provided. For example:

```python
from pydantic import BaseModel
from pydantic_factories import ModelFactory, PostGenerated
from random import randint
from datetime import datetime, timedelta


def add_timedelta(name: str, values: dict, *args, **kwds):
    delta = timedelta(days=randint(0, 12), seconds=randint(13, 13000))
    return values["from_dt"] + delta


class MyModel(BaseModel):
    from_dt: datetime
    to_dt: datetime


class MyFactory(ModelFactory):
    __model__ = MyModel

    to_dt = PostGenerated(add_timedelta)
```

The signature for use is: `cb: Callable, *args, **defaults`, it can receive any sync callable. The signature
for the callable should be: `name: str, values: dict[str, Any], *args, **defaults`. The already generated
values are mapped by name in the `values` dictionary.

#### Ignore (field)

`Ignore` is another field exported by this library, and its used - as its name implies - to designate a given attribute
as ignored:

```python
from typing import TypeVar

from odmantic import EmbeddedModel, Model
from pydantic_factories import ModelFactory, Ignore

T = TypeVar("T", Model, EmbeddedModel)


class OdmanticModelFactory(ModelFactory[T]):
    id = Ignore()
```

The above example is basically the extension included in `pydantic-factories` for the
library [ODMantic](https://github.com/art049/odmantic), which is a pydantic based mongo ODM.

For ODMantic models, the `id` attribute should not be set by the factory, but rather handled by the odmantic logic
itself. Thus, the `id` field is marked as ignored.

When you ignore an attribute using `Ignore`, it will be completely ignored by the factory - that is, it will not be set
as a kwarg passed to pydantic at all.

#### Require (field)

The `Require` field in turn specifies that a particular attribute is a **required kwarg**. That is, if a kwarg with a
value for this particular attribute is not passed when calling `factory.build()`, a `MissingBuildKwargError` will be
raised.

What is the use case for this? For example, lets say we have a document called `Article` which we store in some DB and
is represented using a non-pydantic model, say, an `elastic-dsl` document. We then need to store in our pydantic object
a reference to an id for this article. This value should not be some mock value, but must rather be an actual id passed
to the factory. Thus, we can define this attribute as required:

```python
from pydantic import BaseModel
from pydantic_factories import ModelFactory, Require
from uuid import UUID


class ArticleProxy(BaseModel):
    article_id: UUID
    ...


class ArticleProxyFactory(ModelFactory):
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
from pydantic_factories import ModelFactory
from typing import TypeVar, List

from pydantic import BaseModel
from pydantic_factories import SyncPersistenceProtocol, AsyncPersistenceProtocol

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
from pydantic_factories import ModelFactory
from typing import TypeVar, List

from pydantic import BaseModel
from pydantic_factories import SyncPersistenceProtocol, AsyncPersistenceProtocol

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
from pydantic_factories import ModelFactory


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

## Extensions and Third Party Libraries

Any class that is derived from pydantic's `BaseModel` can be used as the `__model__` of a factory. For most 3rd party
libraries, e.g. [SQLModel](https://sqlmodel.tiangolo.com/), this library will work as is out of the box.

Currently, this library also includes the following extensions:

### ODMantic

This extension includes a class called `OdmanticModelFactory` and it can be imported from `pydantic_factory.extensions`.
This class is meant to be used with the `Model` and `EmbeddedModel` classes exported by ODMantic, but it will also work
with regular instances of pydantic's `BaseModel`.

### Beanie

This extension includes a class called `BeanieDocumentFactory` as well as an `BeaniePersistenceHandler`. Both of these
can be imported from `pydantic_factory.extensions`. The `BeanieDocumentFactory` is meant to be used with the
Beanie `Document` class, and it includes async persistence build in.

### Ormar

This extension includes a class called `OrmarModelFactory`. This class is meant to be used with the `Model` class
exported by ormar.

### Adding Factory Values

If your model has an attribute that is not supported by `pydantic-factories` and
it depends on third party libraries, you can create your custom extension
subclassing the `ModelFactory`, and overriding the `get_mock_value` method to
add your logic.

```python
from typing import Any
from pydantic_factories import ModelFactory


class CustomFactory(ModelFactory[Any]):
    """Tweak the ModelFactory to add our custom mocks."""

    @classmethod
    def get_mock_value(cls, field_type: Any) -> Any:
        """Add our custom mock value."""
        if str(field_type) == "my_super_rare_datetime_field":
            return cls.get_faker().date_time_between()

        return super().get_mock_value(field_type)
```

Where `cls.get_faker()` is a `faker` instance that you can use to build your
returned value.

## Plugins

### Pytest

Any class from `ModelFactory` can use the decorator to register as a fixture easily.

The model factory will be registered as a fixture with the name in snake case.

e.g. `PersonFactory` -> `person_factory`

The decorator also provides some pytest-like arguments to define the fixture. (`scope`, `autouse`, `name`)

```py
from datetime import date, datetime
from typing import List, Union

from pydantic import UUID4, BaseModel

from pydantic_factories import ModelFactory
from pydantic_factories.plugins.pytest_plugin import register_fixture


class Person(BaseModel):
    id: UUID4
    name: str
    hobbies: List[str]
    age: Union[float, int]
    birthday: Union[datetime, date]


@register_fixture
class PersonFactory(ModelFactory):
    """A person factory"""

    __model__ = Person


@register_fixture(scope="session", autouse=True, name="cool_guy_factory")
class AnotherPersonFactory(ModelFactory):
    """A cool guy factory"""

    __model__ = Person


def test_person_factory(person_factory: PersonFactory) -> None:
    person = person_factory.build()
    assert isinstance(person, Person)


def test_cool_guy_factory(cool_guy_factory: AnotherPersonFactory) -> None:
    cool_guy = cool_guy_factory.build()
    assert isinstance(cool_guy, Person)
```

Use `pytest --fixtures` will show output along these lines:

```sh
------------- fixtures defined from pydantic_factories.plugins.pytest_plugin -------------
cool_guy_factory [session scope] -- pydantic_factories/plugins/pytest_plugin.py:48
    A cool guy factory

person_factory -- pydantic_factories/plugins/pytest_plugin.py:48
    A person factory

```

## Partial parameters random generation

Pydantic factories can randomly generate missing parameters for child factories. Example, given the following models and PersonFactory factory:

```python
from pydantic_factories import ModelFactory
from pydantic import BaseModel


class Pet(BaseModel):
    name: str
    age: int


class Person(BaseModel):
    name: str
    pets: list[Pet]
    age: int


class PersonFactory(ModelFactory[Person]):
    __model__ = Person
```

When building a person without specifying the Person and pets ages, all these age fields are randomly generated:

```python
from pydantic_factories import ModelFactory
from pydantic import BaseModel


class Pet(BaseModel):
    name: str
    age: int


class Person(BaseModel):
    name: str
    pets: list[Pet]
    age: int


class PersonFactory(ModelFactory[Person]):
    __model__ = Person


data = {
    "name": "John",
    "pets": [
        {"name": "dog"},
        {"name": "cat"},
    ],
}

person = PersonFactory.build(**data)

print(person.json(indent=2))
```

```json
{
  "name": "John",
  "pets": [
    {
      "name": "dog",
      "age": 9005
    },
    {
      "name": "cat",
      "age": 2455
    }
  ],
  "age": 975
}
```

## Frequently Asked Questions (FAQs)

- How does this differ from using the [Hypothesis plugin](https://pydantic-docs.helpmanual.io/hypothesis_plugin/) for Pydantic?
  This library is closer to [FactoryBoy](https://github.com/FactoryBoy/factory_boy) than Hypothesis (intended for property based testing) by enabling you to define reusable factories. It is possible to use Hypothesis strategies to build your model via `st.builds(Model)`, and even wrap these strategies for re-use, but if you want to share these outside of your codebase you will need to make a library.

- Why doesn't this library use Hypothesis?
  Hypothesis is a large dependency with many features this library does not need and only supports a subset of Pydantic types.

Pydantic Factories uses [Faker](https://faker.readthedocs.io/en/master/) to handle some data mocking, while also incorporating its own mock data generation logic to go beyond what Faker is capable of and providing more complete support for Pydantic types than both Hypothesis and the official Pydantic Hypothesis plugin.

Finally, this library allows for more granular control of model generation and persistence.
