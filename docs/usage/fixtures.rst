Pytest fixtures
===============

Polyfactory support registering factories as pytest fixtures using the
:func:`register_fixture <polyfactory.pytest_plugin.register_fixture>` decorator:

.. literalinclude:: /examples/fixtures/test_example_1.py
    :caption: Using the ``register_fixture_decorator`` field.
    :language: python

In the above example the ``PersonFactory`` is wrapped as a pytest fixture. As a result it cannot be used as a normal
factory,because pytest fixtures are callables that must be called by pytest. To overcome this restriction, you can
declare the fixture separately from the declaration of the class:

.. literalinclude:: /examples/fixtures/test_example_2.py
    :caption: Using the ``register_fixture_decorator`` field without wrapping the factory class.
    :language: python

You can also control the name of the fixture using the optional ``name`` kwarg:

.. literalinclude:: /examples/fixtures/test_example_3.py
    :caption: Aliasing a factory fixture using the `name` kwarg.
    :language: python


The ``Fixture`` Field
---------------------

You can also use factory fixtures as factory fields using the :class:`Fixture <polyfactory.pytest_plugin.FactoryFixture>`:

.. literalinclude:: /examples/fixtures/test_example_4.py
    :caption: Using the ``Fixture`` field.
    :language: python

``Fixture`` is similar to ``Use`` in that it accepts kwargs that are propagated the to the build or batch methods of the
factory.
