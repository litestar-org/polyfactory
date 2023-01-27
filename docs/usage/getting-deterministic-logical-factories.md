# Getting Deterministic Logical Values

In this following example we create a factory for a person model

```py
class Person(BaseModel):
    name: str
    age: int
```
If we use the factory class:

```py
class PersonFactory(ModelFactory):
    __model__ = Person
```

We can get values like this:

```json
{
  "values": [
    {
      "name": "GMPXMVbyXHUfymCDaloV",
      "age": 6380
    },
    {
      "name": "iPhGgaTklZTpXCJkWJYU",
      "age": 4895
    },
    {
      "name": "bvWnrQEEKdspKjyjnWXs",
      "age": 6623
    }
  ]
}
```

So we have 2 problems with that.<br>
The next run will lead to completely different values.<br>
The values are not logical (age=6623)

## Using Seed & Choice

First, we need to make the random part deterministic. We can achieve that like this:

```py
import random
from faker import Faker
Faker.seed(10)
random.seed(10)
```


Now let’s make the values logical:
```py
my_faker = Faker()

class PersonFactory(ModelFactory):
    __faker__ = my_faker
    __model__ = Person

    name = Use(choice, ["Ralph", "Roxy", "Roy", "Ronald", "Rose"])
    age = Use(choice, range(10, 80))
```

And now it make more sense:<br>
```json
{
  "values": [
    {
      "name": "Ralph",
      "age": 64
    },
    {
      "name": "Ronald",
      "age": 11
    },
    {
      "name": "Roxy",
      "age": 68
    }
  ]
}
```
## Full Example

```py
import random
from pprint import pprint as print
from random import choice

from faker import Faker
from pydantic import BaseModel
from pydantic_factories import ModelFactory, Use

Faker.seed(10)
random.seed(10)
my_faker = Faker()


class Person(BaseModel):
    name: str
    age: int


class PersonFactory(ModelFactory):
    __faker__ = my_faker
    __model__ = Person

    name = Use(choice, ["Ralph", "Roxy", "Roy", "Ronald", "Rose"])
    age = Use(choice, range(10, 80))


if __name__ == '__main__':
    print(PersonFactory.batch(size=5))
```
