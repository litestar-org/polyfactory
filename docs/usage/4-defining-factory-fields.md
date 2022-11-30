# Defining Factory Fields

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

## Use

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

## Global factory registration

Sometimes you want to alter how model is built by default. It is especially useful for a model that is used a lot across the project. In this case updating attributes to reference specific factory everywhere can be quite cumbersome. Instead
you can rely on auto registering models by setting the `__auto_register__` attribute`.

```python
from datetime import date, datetime
from pydantic import BaseModel, UUID4
from typing import Any, Dict, List, Union
from enum import Enum
from pydantic_factories import ModelFactory
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
    __auto_register__ = True

    name = lambda: choice(["Ralph", "Roxy"])  # noqa: E731
    species = Species.DOG


class PersonFactory(ModelFactory):
    __model__ = Person
```

Here if we call `PersonFactory.build()` the result will be randomly generated except the pet list which will
contain a dog with name `Ralph` or `Roxy`. Notice that in this case we didn't have to define `pets` attribute
in the `PersonFactory` because we have registered `PetFactory` as the default factory for the `Pet` model.

## PostGenerated

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

## Ignore

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

## Require

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

## Fixture

The `Fixture` field is a special field meant to be used with factories that have been decorated using
[register_fixture](./8-pytest-fixtures.md). For example:

```python
from typing import Optional, List, Union
from datetime import datetime, date
from pydantic import BaseModel, UUID4
from pydantic_factories import ModelFactory, Fixture
from pydantic_factories.plugins.pytest_plugin import register_fixture


class Person(BaseModel):
    id: UUID4
    name: str
    hobbies: Optional[List[str]]
    nicks: List[str]
    age: Union[float, int]
    birthday: Union[datetime, date]


class ClassRoom(BaseModel):
    teacher: Person
    pupils: List[Person]


@register_fixture(name="my_fixture")
class PersonFactory(ModelFactory):
    __model__ = Person


class ClassRoomFactory(ModelFactory):
    teacher = Fixture(PersonFactory, name="Jenny Osterman")
    pupils = Fixture(PersonFactory, size=20)
```

If we tried to use `PersonFactory` now normally it wouldn't work because pytest fixtures can only be called by pytest.
Thus we can use `Fixture`. As you can see above, this field can accept kwargs that are passed to the factory's
underlying build or batch methods, and an optional `size` kwarg. If `size` is given, than a batch is returned, otherwise
the normal build method is used.
