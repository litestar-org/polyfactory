# Changelog

[0.1.0a]

- core functionalities, including build and batch methods.

[0.2.0a]

- implemented handling of all pydantic constraint fields.

[0.3.0b]

- initial MvP release.

[0.3.1b]

- fix issues with decimal parsing.

[0.3.2b]

- add beanie extension.
- removed support for python 3.6.

[0.3.3b]

- fix TypeError being raised from issubclass() for python 3.9+.

[0.3.4b]

- add Ignore and Require fields.
- add support for ODMantic.
- add support for forward refs.

[0.3.5b]

- update fields.
- update readme.

[0.4.0]

- add support for dataclasses.

[0.4.1]

- update random return None values for Optional[] marked fields.

[0.4.2]

- update handling of dataclasses to support randomized optionals.

[0.4.3]

- fix `py.typed` not placed inside the package.

[0.4.4]

- update exports to be explicit.

[0.4.5]

- fix generation of enum in complex types.

[0.4.6]

- fix generation of nested constrained fields.

[0.5.0]

- add ormar extension.

[0.6.0]

- add `__allow_none_optionals__` factory class variable.
- add a new method on `ModelFactory` called `should_set_none_value`, which dictates whether a None value should be set for a given `ModelField`
- update dependencies.
- update the `ModelFactory.create_factory` method to accept an optional `base` kwarg user defined kwargs.

[0.6.1]

- fix bug were nested optionals did not factor in `__allow_none_optionals__` settings.

[0.6.2]

- fix bug with Literal[] values not being recognized.

[0.6.3]

- fix backwards compatible import.

[0.7.0]

- add support for `factory_use_construct` kwargs, thanks - @danielkatzan.

[0.8.0]

- add random configuration. Thanks to @eviltnan.

[1.0.0]

- update to support pydantic 1.9.0, including all new types.

[1.1.0]

- add support for constrained frozenset.
- fix compatibilities issues with pydantic 1.8.2.

[1.2.0]

- add support for naive classes (including all builtin exceptions).
- fix factory typing and resolve issue with TypeVars not being bounded, @lindycoder.
- fix the `create_model_factory` method to use the current `cls` as the created factory's base by default.

[1.2.1]

- fix NameError that can occur when calling `update_forward_refs` without access to a localNS.

[1.2.2]

- add `Any` to Providers.

[1.2.3]

- fix regression due to lambda function argument.

[1.2.4]

- update dependencies,

[1.2.5]

- fix handling of FKs for ormar extension,
- fix handling of choice for ormar extension @mciszczon,

[1.2.6]

- fix handling of decimal mac length @DaanRademaker.

[1.2.7]

- fix checking of Union types in python 3.10 using pipe operator @DaanRademaker.

[1.2.8]

- update random seed to affect exrex @blagasz.

[1.2.9]

- add `allow_population_by_field_name` flag @mrkovalchuk.
- update to pydantic 1.9.1.

[1.3.0]

- a `PostGenerate` @blagasz.

[1.4.0]

- replace `exrex` with `xeger` due to licensing issues.

[1.4.1]

- fix sampling of `Literal` values.

[1.5.0]

- handle partial attributes factory for child factories solving issue #50 @phbernardes.

[1.5.1]

- fix error when building with a parameter that is a pydantic model @phbernardes.
- update typing and cast calls to use TYPE_CHECKING blocks.

[1.5.2]

- fix error when building with a parameter that is an optional pydantic model @phbernardes.

[1.5.3]

- fix error with decimal validation.

[1.5.4]

- fix error when building with a parameter that is an optional pydantic model @phbernardes.

[1.6.0]

- update pydantic version to `1.9.2` and restrict version range to `>=1.9.0`.

[1.6.1]

- updated pydantic version to `1.10.0`.

[1.6.2]

- fix random-seed doesn't affect UUID generation.

[1.7.0]

- add Python `3.11` support.

[1.7.1]

- fix passing dictionaries with nested pydantic models.

[1.8.0]

- add support for automatic pytest fixture creation @EltonChou.
- add support for plugins @EltonChou.

[1.8.1]

- fix recursion exception with discriminated unions.

[1.8.2]

- fix `pytest` being a required dependency.

[1.9.0]

- update `ModelFactory` to expose `get_faker()`.

[1.10.0]

- add support for `ConstrainedDate`.
