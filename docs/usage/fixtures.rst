Pytest fixtures
===============

Polyfactory support registering factories as pytest fixtures using the
:func:`register_fixture <polyfactory.pytest_plugin.register_fixture>` decorator:

.. literalinclude:: /examples/fixtures/test_example_1.py
    :caption: Using the ``register_fixture_decorator`` field.
    :language: python

The fixture can be registered separately from the declaration of the class. This is useful when a different pytest fixture location to where the factory is defined.

.. literalinclude:: /examples/fixtures/test_example_2.py
    :caption: Using the ``register_fixture_decorator`` field separately.
    :language: python

You can also control the name of the fixture using the optional ``name`` kwarg:

.. literalinclude:: /examples/fixtures/test_example_3.py
    :caption: Aliasing a factory fixture using the `name` kwarg.
    :language: python
