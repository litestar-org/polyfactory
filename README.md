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

<!-- ALL-CONTRIBUTORS-BADGE:START - Do not remove or modify this section -->

[![All Contributors](https://img.shields.io/badge/all_contributors-8-orange.svg?style=flat-square)](#contributors-)

<!-- ALL-CONTRIBUTORS-BADGE:END -->

</div>
<!-- markdownlint-restore -->

Polyfactory is a simple and powerful mock data generation library, based around type
hints and supporting dataclasses, typed-dicts, pydantic models, msgspec structs and more.

Polyfactory part of the Litestar project and as such actively maintained by a community of maintainers and contributors.

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

That's it - with almost no work, we are able to create a mock data object fitting the `Person` class model definition.

This is possible because of the typing information available on the dataclass, which are used as a
source of truth for data generation.

The factory parses the information stored in the dataclass and generates a dictionary of kwargs that are passed to
`Person`.

## Documentation

Usage and API reference documentation is available on https://polyfactory.litestar.dev/.

## Installation

```shell
pip install polyfactory
```

## Relation to Pydantic-Factories

Prior to version 2, this library was known as [pydantic-factories](https://pypi.org/project/pydantic-factories/), a name
under which it gained quite a bit of popularity.
A main motivator for the 2.0 release was that we wanted to support more than just Pydantic models, something which also
required a change to its core architecture. As this library would no longer be directly tied to Pydantic, `polyfactory`
was chosen as its new name to reflect its capabilities; It can generate mock data for dataclasses, typed-dicts,
Pydantic, odmantic, and beanie ODM models, as well as custom factories.

## Contributing

This library is a community driven open source project. We welcome and encourage contributions. Please checkout the
GitHub issues, read the contribution guide (at the repository's root), and you're always welcome
to [join our discord server](https://discord.gg/F4jPQzHpBU).

## Contributors ✨

Thanks goes to these wonderful people ([emoji key](https://allcontributors.org/docs/en/emoji-key)):

<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
<!-- prettier-ignore-start -->
<!-- markdownlint-disable -->
<table>
  <tbody>
    <tr>
      <td align="center" valign="top" width="14.28%"><a href="https://scriptr.dev/"><img src="https://avatars.githubusercontent.com/u/45884264?v=4?s=100" width="100px;" alt="Jacob Coffee"/><br /><sub><b>Jacob Coffee</b></sub></a><br /><a href="#infra-JacobCoffee" title="Infrastructure (Hosting, Build-Tools, etc)">🚇</a> <a href="https://github.com/litestar-org/polyfactory/commits?author=JacobCoffee" title="Tests">⚠️</a> <a href="https://github.com/litestar-org/polyfactory/commits?author=JacobCoffee" title="Code">💻</a> <a href="https://github.com/litestar-org/polyfactory/commits?author=JacobCoffee" title="Documentation">📖</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/provinzkraut"><img src="https://avatars.githubusercontent.com/u/25355197?v=4?s=100" width="100px;" alt="Janek Nouvertné"/><br /><sub><b>Janek Nouvertné</b></sub></a><br /><a href="#infra-provinzkraut" title="Infrastructure (Hosting, Build-Tools, etc)">🚇</a> <a href="https://github.com/litestar-org/polyfactory/commits?author=provinzkraut" title="Tests">⚠️</a> <a href="https://github.com/litestar-org/polyfactory/commits?author=provinzkraut" title="Code">💻</a> <a href="#design-provinzkraut" title="Design">🎨</a> <a href="https://github.com/litestar-org/polyfactory/commits?author=provinzkraut" title="Documentation">📖</a> <a href="#maintenance-provinzkraut" title="Maintenance">🚧</a> <a href="#projectManagement-provinzkraut" title="Project Management">📆</a> <a href="https://github.com/litestar-org/polyfactory/pulls?q=is%3Apr+reviewed-by%3Aprovinzkraut" title="Reviewed Pull Requests">👀</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/Goldziher"><img src="https://avatars.githubusercontent.com/u/30733348?v=4?s=100" width="100px;" alt="Na'aman Hirschfeld"/><br /><sub><b>Na'aman Hirschfeld</b></sub></a><br /><a href="#infra-Goldziher" title="Infrastructure (Hosting, Build-Tools, etc)">🚇</a> <a href="https://github.com/litestar-org/polyfactory/commits?author=Goldziher" title="Tests">⚠️</a> <a href="https://github.com/litestar-org/polyfactory/commits?author=Goldziher" title="Code">💻</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://czaplicki.it/"><img src="https://avatars.githubusercontent.com/u/9108586?v=4?s=100" width="100px;" alt="Marek Czaplicki"/><br /><sub><b>Marek Czaplicki</b></sub></a><br /><a href="https://github.com/litestar-org/polyfactory/commits?author=mdczaplicki" title="Code">💻</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/przybylop"><img src="https://avatars.githubusercontent.com/u/82805821?v=4?s=100" width="100px;" alt="Piotr Przybyło"/><br /><sub><b>Piotr Przybyło</b></sub></a><br /><a href="https://github.com/litestar-org/polyfactory/commits?author=przybylop" title="Code">💻</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/sygutss"><img src="https://avatars.githubusercontent.com/u/48909366?v=4?s=100" width="100px;" alt="sygutss"/><br /><sub><b>sygutss</b></sub></a><br /><a href="https://github.com/litestar-org/polyfactory/issues?q=author%3Asygutss" title="Bug reports">🐛</a> <a href="https://github.com/litestar-org/polyfactory/commits?author=sygutss" title="Code">💻</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/chrisbeardy"><img src="https://avatars.githubusercontent.com/u/20585410?v=4?s=100" width="100px;" alt="chrisbeardy"/><br /><sub><b>chrisbeardy</b></sub></a><br /><a href="https://github.com/litestar-org/polyfactory/commits?author=chrisbeardy" title="Documentation">📖</a></td>
    </tr>
    <tr>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/guacs"><img src="https://avatars.githubusercontent.com/u/126393040?v=4?s=100" width="100px;" alt="guacs"/><br /><sub><b>guacs</b></sub></a><br /><a href="https://github.com/litestar-org/polyfactory/commits?author=guacs" title="Code">💻</a></td>
    </tr>
  </tbody>
</table>

<!-- markdownlint-restore -->
<!-- prettier-ignore-end -->

<!-- ALL-CONTRIBUTORS-LIST:END -->

This project follows the [all-contributors](https://github.com/all-contributors/all-contributors) specification.
Contributions of any kind welcome!
