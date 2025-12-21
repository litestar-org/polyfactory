Migration Guide
===============

.. note::
   This guide is for an unrelease version of polyfactory.

For v2 to v3 migration, this is largely deprecation internal parameters and updating defaults to be more aligned with common use cases.

SQLAlchemyFactory Default Changes
---------------------------------

In the latest version, we've made changes to the default behavior of SQLAlchemyFactory to better align with common use cases. Here are the key changes and how to migrate:

Default Relationship Behavior
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Before:**

- ``__set_relationships__`` defaulted to ``False``
- Relationships were not automatically populated unless explicitly enabled

**After:**

- ``__set_relationships__`` now defaults to ``True``
- Relationships are automatically populated by default

To maintain the previous behavior, explicitly set ``__set_relationships__ = False`` on your factory.

Model Validation Behavior
-------------------------

**Before:**

- ``__check_model__`` defaulted to ``False``
- Model structure validation was disabled by default

**After:**

- ``__check_model__`` now defaults to ``True``
- Model structure validation is enabled by default
- This helps catch potential issues with model definitions early

To maintain the previous behavior, explicitly set ``__check_model__ = False`` on your factory.

Fixture Field Removal
---------------------

The ``polyfactory.fields.Fixture`` field has been removed in v3. This was a legacy field that was used to define factory behavior through a separate ``pytest`` fixture.

Instead, all factories can be used directly as `factories as fields <https://polyfactory.litestar.dev/latest/usage/fields.html#factories-as-fields>`_. For batch usage, this can be combined with ``Use`` or similar.

Internal Parameter Changes
--------------------------

Several internal parameters have been removed or changed in v3 to simplify ``FieldMeta`` and typing utils to be deterministic. Usage of ``random.Random`` parameters should be removed as per warning emitted.
