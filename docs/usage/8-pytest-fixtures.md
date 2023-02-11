# Using Factories as Fixtures

Any class from `ModelFactory` can use the decorator to register as a fixture easily.

The model factory will be registered as a fixture with the name in snake case.

e.g. `PersonFactory` -> `person_factory`

The decorator also provides some pytest-like arguments to define the fixture. (`scope`, `autouse`, `name`)

```py
from datetime import date, datetime
from typing import List, Union

from pydantic import UUID4, BaseModel

from polyfactory.factories.pydantic_factory import ModelFactory
from polyfactory.pytest_plugin import register_fixture


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
------------- fixtures defined from polyfactory.plugins.pytest_plugin -------------
cool_guy_factory [session scope] -- polyfactory/plugins/pytest_plugin.py:48
    A cool guy factory

person_factory -- polyfactory/plugins/pytest_plugin.py:48
    A person factory

```
