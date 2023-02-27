<!-- markdownlint-disable -->
<p align="center">
  <img src="https://github.com/starlite-api/branding/blob/9ab099a2089219c07727baaa29f67e9474ff93c8/assets/Starlite%20Branding%20-%20SVG%20-%20Transparent/Logo%20-%20Banner%20-%20Inline%20-%20Light.svg#gh-light-mode-only" alt="Starlite Logo - Light" width="100%" height="auto" />
  <img src="https://github.com/starlite-api/branding/blob/9ab099a2089219c07727baaa29f67e9474ff93c8/assets/Starlite%20Branding%20-%20SVG%20-%20Transparent/Logo%20-%20Banner%20-%20Inline%20-%20Dark.svg#gh-dark-mode-only" alt="Starlite Logo - Dark" width="100%" height="auto" />
</p>
<!-- markdownlint-restore -->

<!-- markdownlint-disable -->
<div align="center">

![PyPI - License](https://img.shields.io/pypi/l/pydantic-factories?color=blue)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pydantic-factories)

[![Coverage](https://sonarcloud.io/api/project_badges/measure?project=starlite-api_pydantic-factories&metric=coverage)](https://sonarcloud.io/summary/new_code?id=starlite-api_pydantic-factories)
[![Maintainability Rating](https://sonarcloud.io/api/project_badges/measure?project=starlite-api_pydantic-factories&metric=sqale_rating)](https://sonarcloud.io/summary/new_code?id=starlite-api_pydantic-factories)
[![Reliability Rating](https://sonarcloud.io/api/project_badges/measure?project=starlite-api_pydantic-factories&metric=reliability_rating)](https://sonarcloud.io/summary/new_code?id=starlite-api_pydantic-factories)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=starlite-api_pydantic-factories&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=starlite-api_pydantic-factories)

[![Discord](https://img.shields.io/discord/919193495116337154?color=202235&label=%20Discord&logo=discord)](https://discord.gg/X3FJqy8d2j) [![Matrix](https://img.shields.io/badge/%5Bm%5D%20Matrix-bridged-blue?color=202235)](https://matrix.to/#/#starlitespace:matrix.org) [![Reddit](https://img.shields.io/reddit/subreddit-subscribers/starlite?label=r%2FStarlite&logo=reddit)](https://reddit.com/r/starlite)

</div>
<!-- markdownlint-restore -->

# Pydantic-Factories

This library offers powerful mock data generation capabilities for [pydantic](https://github.com/samuelcolvin/pydantic)
based models, `dataclasses` and `TypeDict`s. It can also be used with other libraries that use pydantic as a foundation.

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
- ✅ supports TypedDicts

## Why This Library?

- 💯 powerful
- 💯 extensible
- 💯 simple
- 💯 rigorously tested

## Contributing

This library is open to contributions - in fact we welcome it. [Please see the contribution guide!](CONTRIBUTING.md)
