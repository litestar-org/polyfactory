<!-- markdownlint-disable -->
<img alt="Starlite logo" src="./starlite-banner.svg" width="100%" height="auto">
<!-- markdownlint-restore -->

<!-- markdownlint-disable -->
<div align="center">

![PyPI - License](https://img.shields.io/pypi/l/pydantic-factories?color=blue)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pydantic-factories)

[![Language grade: Python](https://img.shields.io/lgtm/grade/python/g/Goldziher/pydantic-factories.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/Goldziher/pydantic-factories/context:python)
[![Total alerts](https://img.shields.io/lgtm/alerts/g/Goldziher/pydantic-factories.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/Goldziher/pydantic-factories/alerts/)
[![Coverage](https://sonarcloud.io/api/project_badges/measure?project=starlite-api_pydantic-factories&metric=coverage)](https://sonarcloud.io/summary/new_code?id=starlite-api_pydantic-factories)
[![Maintainability Rating](https://sonarcloud.io/api/project_badges/measure?project=starlite-api_pydantic-factories&metric=sqale_rating)](https://sonarcloud.io/summary/new_code?id=starlite-api_pydantic-factories)
[![Reliability Rating](https://sonarcloud.io/api/project_badges/measure?project=starlite-api_pydantic-factories&metric=reliability_rating)](https://sonarcloud.io/summary/new_code?id=starlite-api_pydantic-factories)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=starlite-api_pydantic-factories&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=starlite-api_pydantic-factories)

[![Discord](https://img.shields.io/discord/919193495116337154?color=blue&label=chat%20on%20discord&logo=discord)](https://discord.gg/X3FJqy8d2j)

</div>
<!-- markdownlint-restore -->

# Pydantic-Factories

This library offers powerful mock data generation capabilities for [pydantic](https://github.com/samuelcolvin/pydantic)
based models and `dataclasses`. It can also be used with other libraries that use pydantic as a foundation.

Check out [the documentation 📚](https://starlite-api.github.io/pydantic-factories/).

## Installation

```shell
pip install pydantic-factories
```

## Example

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

## Features

- ✅ supports both built-in and pydantic types
- ✅ supports pydantic field constraints
- ✅ supports complex field types
- ✅ supports custom model fields
- ✅ supports dataclasses

## Why This Library?

- 💯 powerful
- 💯 extensible
- 💯 simple
- 💯 rigorously tested

## Contributing

This library is open to contributions - in fact we welcome it. [Please see the contribution guide!](CONTRIBUTING.md)
