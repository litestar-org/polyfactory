# Polyfactory

<!-- markdownlint-disable -->
<p align="center">
  <img src="https://github.com/litestar-org/branding/blob/e27cda904e0649e5065ac1c26df6a279ba5d06b5/assets/Branding%20-%20SVG%20-%20Transparent/Polyfactory%20-%20Banner%20-%20Inline%20-%20Light.svg#gh-light-mode-only" alt="Litestar - Polyfactory Logo - Light" width="100%" height="auto" />
  <img src="https://github.com/litestar-org/branding/blob/e27cda904e0649e5065ac1c26df6a279ba5d06b5/assets/Branding%20-%20SVG%20-%20Transparent/Polyfactory%20-%20Banner%20-%20Inline%20-%20Dark.svg#gh-dark-mode-only" alt="Litestar - Polyfactory Logo - Dark" width="100%" height="auto" />
</p>
<!-- markdownlint-restore -->

<!-- markdownlint-disable -->
<div align="center">

![PyPI - License](https://img.shields.io/pypi/l/polyfactory?color=blue)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/polyfactory)

[![Coverage](https://sonarcloud.io/api/project_badges/measure?project=starlite-api_polyfactory&metric=coverage)](https://sonarcloud.io/summary/new_code?id=litestar-org_polyfactory)
[![Maintainability Rating](https://sonarcloud.io/api/project_badges/measure?project=starlite-api_polyfactory&metric=sqale_rating)](https://sonarcloud.io/summary/new_code?id=litestar-org_polyfactory)
[![Reliability Rating](https://sonarcloud.io/api/project_badges/measure?project=starlite-api_polyfactory&metric=reliability_rating)](https://sonarcloud.io/summary/new_code?id=litestar-org_polyfactory)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=starlite-api_polyfactory&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=litestar-org_polyfactory)
[![Security Rating](https://sonarcloud.io/api/project_badges/measure?project=starlite-api_polyfactory&metric=security_rating)](https://sonarcloud.io/summary/new_code?id=litestar-org_polyfactory)

[![Reddit](https://img.shields.io/reddit/subreddit-subscribers/litestar?label=r%2FLitestar&logo=reddit)](https://reddit.com/r/litestar-api)
[![Discord](https://img.shields.io/discord/919193495116337154?color=blue&label=chat%20on%20discord&logo=discord)](https://discord.gg/X3FJqy8d2j)
[![Matrix](https://img.shields.io/badge/%5Bm%5D%20chat%20on%20Matrix-bridged-blue)](https://matrix.to/#/#litestar:matrix.org)
[![Medium](https://img.shields.io/badge/Medium-12100E?style=flat&logo=medium&logoColor=white)](https://blog.litestar.dev)

</div>
<!-- markdownlint-restore -->

This library offers factories for mock data generation using python type hints. It part of the LiteStar-API project and
is actively maintained by a community of maintainers and contributors.

## Example

```python
from dataclasses import dataclass

from polyfactory.factories import DataclassFactory


@dataclass
class Person:
    name: str
    age: float
    height: float
    weight: float


class PersonFactory(DataclassFactory[Person]):
    __model__ = Person


def test_is_person() -> None:
    person_instance = PersonFactory.build()
    assert isinstance(person_instance, Person)
```

That's it - with almost no work, we are able to create a mock data object fitting the Person class model definition.

This is possible because of the typing information available on the dataclass, which are used as a
source of truth for data generation.

The factory parses the information stored in the dataclass and generates a dictionary of kwargs that are passed to
the Person class constructor.

## Documentation

A full API reference and usage documentation is available in
the [dedicated documentation site](https://polyfactory.litestar.dev/).

## Installation

```shell
pip install polyfactory
```

## Relation to Pydantic-Factories

The earlier version of this library was released under the
name [pydantic-factories](https://pypi.org/project/pydantic-factories/).
While this library became very popular (above 100K monthly downloads), we decided to rename it because we changed the
core architecture -
`polyfactory` is a fitting name because we no longer rely on pydantic, which is now an optional dependency. This library
is capable of
generating mock data for dataclasses, typed-dicts and any custom factory using type annotations.
It also supports using pydantic models - but that is optional.

## Contributing

This library is a community driven open source project. We welcome and encourage contributions. Please checkout the
GitHub issues, read the contribution guide (at the repository's root), and you're always welcome
to [join our discord server](https://discord.gg/F4jPQzHpBU).
