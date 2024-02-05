Factory Configuration
=====================

Factories can be configured by setting special dunder (double underscore) class attributes.
You can read the reference for these in the API reference for
:class:`BaseFactory <polyfactory.factories.base.BaseFactory>`. Below we discuss some configuration options in some depth.

Seeding Randomness
------------------

.. literalinclude:: /examples/configuration/test_example_1.py
    :caption: Seeding the factory's 'random.Random'
    :language: python

Seeding randomness allows you to control the random generation of values produced by the factory. This affects all :class:`random.Random`
methods as well as faker.

Setting Random
--------------

.. literalinclude:: /examples/configuration/test_example_2.py
    :caption: Setting the factory's 'random.Random'
    :language: python

This configuration option is functionally identical to the previous, with the difference being that here we are setting
the actual instance of :class:`random.Random`. This is useful when embedding factories inside more complex logic, such as in
other libraries, as well as when factories are being dynamically generated.

Setting Faker
-------------

.. literalinclude:: /examples/configuration/test_example_3.py
    :caption: Setting the factory's 'Faker'
    :language: python

In the above example we are setting the factory's instance of ``Faker`` and configure its locale to Spanish. Because
we are also setting the random seed value, the results of the test are deterministic.

.. note::
    To understand why we are using a classmethod here, see the documentation about :doc:`factory fields </usage/fields>`.

Persistence Handlers
--------------------

Factory classes have four optional persistence methods:

- ``.create_sync(**kwargs)`` - builds and persists a single instance of the factory's model synchronously
- ``.create_batch_sync(size: int, **kwargs)`` - builds and persists a list of size n instances synchronously
- ``.create_async(**kwargs)`` - builds and persists a single instance of the factory's model asynchronously
- ``.create_batch_async(size: int, **kwargs)`` - builds and persists a list of size n instances asynchronously

To use these methods, you must first specify a sync and/or async persistence handlers for the factory:

.. literalinclude:: /examples/configuration/test_example_4.py
    :caption: Defining and using persistence handlers.
    :language: python

With the persistence handlers in place, you can now use all persistence methods.

.. note::
    You do not need to define both persistence handlers. If you will only use sync or async persistence, you only need
    to define the respective handler to use these methods.

Defining Default Factories
--------------------------

As explained in the section about dynamic factory generation in :doc:`declaring factories </usage/declaring_factories>`,
factories generate new factories for supported types dynamically. This process requires no intervention from the user.
Once a factory is generated, it is then cached and reused - when the same type is used.

For example, when build is called for the ``PersonFactory`` below, a ``PetFactory`` will be dynamically generated and reused:

.. literalinclude:: /examples/declaring_factories/test_example_5.py
    :caption: Dynamic factory generation
    :language: python

You can also control the default factory for a type by declaring a factory as the type default:

.. literalinclude:: /examples/configuration/test_example_5.py
    :caption: Setting a factory as a type default.
    :language: python


Randomized Collection Length
----------------------------

Set of fields that allow you to generate a collection with random lengths. By default only one item is generated.


.. literalinclude:: /examples/configuration/test_example_6.py
    :caption: Randomized collection length
    :language: python

Allow None Optionals
--------------------

Allow `None` to be generated as a value for types marked as optional. When set to `True`, the outputted value will be randomly chosen between `None` and other allowed types. By default, this is set to `True`.

By setting to `False`, then optional types will always be treated as the wrapped type:

.. literalinclude:: /examples/configuration/test_example_7.py
    :caption: Disable Allow None Optionals
    :language: python

Check Factory Fields
--------------------
When `__check_model__` is set to `True`, declaring fields on the factory that don't exist on the model will trigger an exception.

This is only true when fields are declared with ``Use``, ``PostGenerated``, ``Ignore`` and ``Require``.
Any other field definition will not be checked.


.. literalinclude:: /examples/configuration/test_example_8.py
    :caption: Enable Check Factory Fields
    :language: python

Use Default Values
------------------

If ``__use_defaults__`` is set to ``True``, then the default value will be used instead of creating a random value
for a given field, provided there's a default value for that field.

By default, ``__use_defaults__`` is set to ``False.`` If you need more fine grained control, you can override the
:meth:`~polyfactory.factories.base.BaseFactory.should_use_default_value` classmethod.

.. note::
    Setting ``__use_defaults__`` has no effect for ``TypedDictFactory`` since you cannot set default values for
    ``TypedDict``.

.. literalinclude:: /examples/configuration/test_example_9.py
    :caption: Use Default Values
    :language: python
