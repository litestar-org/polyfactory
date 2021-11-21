![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pydantic-factories)
[![Coverage](https://sonarcloud.io/api/project_badges/measure?project=Goldziher_pydantic-factories&metric=coverage)](https://sonarcloud.io/summary/new_code?id=Goldziher_pydantic-factories)
[![Maintainability Rating](https://sonarcloud.io/api/project_badges/measure?project=Goldziher_pydantic-factories&metric=sqale_rating)](https://sonarcloud.io/summary/new_code?id=Goldziher_pydantic-factories)
[![Reliability Rating](https://sonarcloud.io/api/project_badges/measure?project=Goldziher_pydantic-factories&metric=reliability_rating)](https://sonarcloud.io/summary/new_code?id=Goldziher_pydantic-factories)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=Goldziher_pydantic-factories&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=Goldziher_pydantic-factories)

# Pydantic Factories

This library offers mock data generation for pydantic based models. This means any user defined models as well as third
party libraries that use pydantic as a foundation, e.g. SQLModel, FastAPI, Beanie, Ormar and others.

### Features

* ✅ supports both built-in and pydantic types
* ✅ supports pydantic field constraints
* ✅ supports complex field typings
* ✅ supports custom model fields

### Why This Library?

* 💯 powerful mock data generation
* 💯 simple to use and extend
* 💯 rigorously tested

## Installation

```sh
pip install pydantic-factories
```

OR

```sh
poetry add --dev pydantic-factories
```

## Usage

```python
from datetime import date, datetime
from typing import List, Union

from pydantic import BaseModel, UUID4

from pydantic_factories.factory import ModelFactory


class Person(BaseModel):
    id: UUID4
    name: str
    hobbies: List[str]
    age: Union[float, int]
    birthday: Union[datetime, date]


class PersonFactoryWithDefaults(ModelFactory):
    __model__ = Person


result = PersonFactoryWithDefaults.build()
```

That's it - the factory will create a data object that fits the defined model and pass it to the pydantic model as
kwargs. It will then pass through the pydantic validation and parsing mechanism, and create a model instance.
