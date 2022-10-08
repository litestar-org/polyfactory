# Changelog

[0.1.0a]

- core functionalities, including build and batch methods

[0.2.0a]

- handling of all pydantic constraint

[0.3.0b]

- full features MvP

[0.3.1b]

- fix issues with decimal parsing

[0.3.2b]

- removed support for python 3.6
- added beanie extension

[0.3.3b]

- resolve TypeError being raised from issubclass() for python 3.9+

[0.3.4b]

- add support for forward refs
- add support for ODMantic
- add Ignore and Require fields

[0.3.5b]

- update readme
- update fields

[0.4.0]

- added support for dataclasses

[0.4.1]

- randomly return None values for Optional[] marked fields

[0.4.2]

- updated handling of dataclasses to support randomized optionals

[0.4.3]

- fixed `py.typed` not placed inside the package

[0.4.4]

- make exports explicit

[0.4.5]

- fix generation of enum in complex types

[0.4.6]

- fix generation of nested constrained fields

[0.5.0]

- add ormar extension

[0.6.0]

- added `__allow_none_optionals__` factory class variable
- updated the `ModelFactory.create_factory` method to accept an optional `base` kwarg user defined \*\*kwargs
- added a new method on `ModelFactory` called `should_set_none_value`, which dictates whether a None value should be set
  for a given `ModelField`
- updated dependencies

[0.6.1]

- fix bug were nested optionals did not factor in `__allow_none_optionals__` settings

[0.6.2]

- fix bug with Literal[] values not being recognized

[0.6.3]

- fix backwards compatible import

[0.7.0]

- added support for `factory_use_construct` kwargs, thanks - @danielkatzan

[0.8.0]

- added random configuration. Thanks to @eviltnan

[1.0.0]

- updated to support pydantic 1.9.0, including all new types

[1.1.0]

- resolve compatibilities issues with pydantic 1.8.2
- add support for constrained frozenset

[1.2.0]

- fix factory typing and resolve issue with TypeVars not being bounded, @lindycoder
- add support for naive classes (including all builtin exceptions)
- fix the `create_model_factory` method to use the current `cls` as the created factory's base by default

[1.2.1]

- suppress NameError that can occur when calling `update_forward_refs` without access to a localNS

[1.2.2]

- added `Any` to Providers

[1.2.3]

- fixed regression due to lambda function argument

[1.2.4]

- updated dependencies

[1.2.5]

- fix handling of choice for ormar extension @mciszczon
- fix handling of FKs for ormar extension

[1.2.6]

- fix handling of decimal mac length @DaanRademaker

[1.2.7]

- fix checking of Union types in python 3.10 using pipe operator @DaanRademaker

[1.2.8]

- update random seed to affect exrex @blagasz

[1.2.9]

- update to pydantic 1.9.1
- handle `allow_population_by_field_name` flag @mrkovalchuk

[1.3.0]

- a `PostGenerate` @blagasz

[1.4.0]

- replace `exrex` with `xeger` due to licensing issues

[1.4.1]

- fix sampling of `Literal` values

[1.5.0]

- Handle partial attributes factory for child factories solving issue #50 @phbernardes

[1.5.1]

- Fix error when building with a parameter that is a pydantic model [Issue #53] @phbernardes
- Update typing and cast calls to use TYPE_CHECKING blocks

[1.5.2]

- Fix error when building with a parameter that is an optional pydantic model [Issue #56] @phbernardes

[1.5.3]

- Fix error with decimal validation

[1.5.4]

- Fix error when building with a parameter that is an optional pydantic model [Issue #56] @phbernardes

[1.6.0]

- Updated pydantic version to `1.9.2`
- Restricted supported pydantic version to `>=1.9.0`

[1.6.1]

- Updated pydantic version to `1.10.0`

[1.6.2]

- Fix random-seed doesn't affect UUID generation

[1.7.0]

- Add Python `3.11` support

[1.7.1]

- Fix passing dictionaries with nested pydantic models

[1.8.0]

- Add support for automatic pytest fixture creation @EltonChou
- Add support for plugins @EltonChou

[1.8.1]

- Fix recursion exception with discriminated unions

[1.8.2]

- Fix `pytest` being a required dependency
