# Build Methods

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

Any `kwargs` you pass to `.build`, `.batch` or any of the [persistence methods](./5-persistence.md), will take precedence over
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

## Partial Parameters

Factories can randomly generate missing parameters for child factories. For example:

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

When building a person without specifying the Person and pets ages, all these fields will be randomly generated:

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
