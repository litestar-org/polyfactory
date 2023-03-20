<!-- markdownlint-disable -->
<p align="center">
  <img src="branding/SVG/polyfactory-banner-inline-light.svg#gh-light-mode-only" alt="Starlite | Polyfactory Logo - Light" width="100%" height="auto" />
  <img src="branding/SVG/polyfactory-banner-inline-dark.svg#gh-dark-mode-only" alt="Starlite | Polyfactory Logo - Dark" width="100%" height="auto" />
</p>
<!-- markdownlint-restore -->

<!-- markdownlint-disable -->
<div align="center">

![PyPI - License](https://img.shields.io/pypi/l/polyfactory?color=blue)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/polyfactory)

[![Coverage](https://sonarcloud.io/api/project_badges/measure?project=starlite-api_polyfactory&metric=coverage)](https://sonarcloud.io/summary/new_code?id=starlite-api_polyfactory)
[![Maintainability Rating](https://sonarcloud.io/api/project_badges/measure?project=starlite-api_polyfactory&metric=sqale_rating)](https://sonarcloud.io/summary/new_code?id=starlite-api_polyfactory)
[![Reliability Rating](https://sonarcloud.io/api/project_badges/measure?project=starlite-api_polyfactory&metric=reliability_rating)](https://sonarcloud.io/summary/new_code?id=starlite-api_polyfactory)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=starlite-api_polyfactory&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=starlite-api_polyfactory)

[![Discord](https://img.shields.io/discord/919193495116337154?color=202235&label=%20Discord&logo=discord)](https://discord.gg/X3FJqy8d2j) [![Matrix](https://img.shields.io/badge/%5Bm%5D%20Matrix-bridged-blue?color=202235)](https://matrix.to/#/#starlitespace:matrix.org) [![Reddit](https://img.shields.io/reddit/subreddit-subscribers/starlite?label=r%2FStarlite&logo=reddit)](https://reddit.com/r/starlite)

</div>
<!-- markdownlint-restore -->

# Polyfactory

This library offers powerful mock data generation capabilities for [pydantic](https://github.com/samuelcolvin/pydantic)
based models, `dataclasses` and `TypeDict`s. It can also be used with other libraries that use pydantic as a foundation.

Check out [the documentation](https://starlite-api.github.io/polyfactory/).

## Installation

```shell
pip install polyfactory
```

## Example

```python
from datetime import date, datetime
from typing import List, Union

from pydantic import BaseModel, UUID4

from polyfactory import ModelFactory


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
#### **Supports**:
- ✅ built-in and pydantic types
- ✅ pydantic field constraints
- ✅ complex field types
- ✅ custom model fields
- ✅ dataclasses
- ✅ TypedDicts

#### Reasons to Choose Polyfactory:
- Powerful
- Easily Extensible
- Simple
- Rigorously Tested

## Contributing

This library is open to contributions - in fact we welcome it. [Please see the contribution guide!](CONTRIBUTING.md)
