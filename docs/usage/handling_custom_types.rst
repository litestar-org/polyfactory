Handling Custom Types
=====================

Sometimes you need to handle custom types, either from 3rd party libraries or from your own codebase. To achieve this,
you can extend what's referred as the `providers_map`:

.. literalinclude:: /examples/handling_custom_types/test_example_1.py
    :caption: Extending the provider map
    :language: python

In the above example we override the `get_provider_map` class method, which maps types to callables. Each callable in the map
returns an appropriate mock value for the type. In the above example, an instance of `CustomSecret` with the hardcoded
string 'jeronimo'.

Creating Custom Base Factories
------------------------------

The above works great when you need to do this in a localised fashion, but if you need to use some custom types in many
places it will lead to unnecessary duplication. The solution for this is to create a custom base factory, in this case
for handling dataclasses:

.. literalinclude:: /examples/handling_custom_types/test_example_2.py
    :caption: Creating a custom dataclass factory with extended provider map
    :language: python

.. note::
    If extra configs values are defined for custom base classes, then ``__config_keys__`` should be extended so
    that these values are correctly passed onto to concrete factories.
