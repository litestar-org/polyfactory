# Nested Models

The automatic generation of mock data works for all types supported by pydantic, as well as nested classes that derive
from `BaseModel` (including for 3rd party libraries) and complex types. Let's look at another example:

```python
from datetime import date, datetime
from enum import Enum
from pydantic import BaseModel, UUID4
from typing import Any, Dict, List, Union

from polyfactory.factories.pydantic_factory import ModelFactory


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
