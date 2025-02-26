Factory Fields
==============

The factory api is designed to be as semantic and simple as possible, and by default it requires no customization to
mock data. Nonetheless, when you do need to customize and control the data being generated, polyfactory has you covered.
Lets look at a few examples:

.. literalinclude:: /examples/fields/test_example_1.py
    :caption: Declaring a PersonFactory with hardcoded pets
    :language: python

In the example above, the call to ``PersonFactory.build()`` results in a ``Person`` where all values are randomly
generated, except the ``pets`` list, which will be the hardcoded value we defined.

The ``Use`` Field
-----------------

This though is often not desirable. We could instead, define a factory for Pet where we restrict the choices to a range
we like. For example:

.. literalinclude:: /examples/fields/test_example_2.py
    :caption: Using the ``Use`` field with a custom PetFactory to control the generation of a Person's pets list
    :language: python

The :class:`Use <polyfactory.fields.Use>` class is merely a semantic abstraction that makes the factory cleaner and simpler
to understand, you can in fact use any callable (including classes) as values for a factory's attribute directly, and
these will be invoked at build-time. Thus, you could for example re-write the above PetFactory like so:

.. literalinclude:: /examples/fields/test_example_3.py
    :caption: Using simple lambda functions to declare custom fields
    :language: python

Or you can use a class method, which will give you easy and nice access to the factory itself:

.. literalinclude:: /examples/fields/test_example_4.py
    :caption: Using class methods to declare custom fields
    :language: python

.. note::
    All the above examples used ``DataclassFactory.__random__.choice``, and this is intentional. While you can use
    ``random.choice`` or any other function exported from the stdlib random library, the factory class has its own instance
    of ``random.Random`` attached under ``cls.__random__``. This instance can be affected by random seeding in several ways, e.g.
    calling the factory seeding method, which will be scoped only to this instance. Thus, for consistent results when seeding
    randomness, its important to use the factory ``random.Random`` instance rather than the global one from the stdlib.

The ``Ignore`` Field
--------------------

:class:`Ignore <polyfactory.fields.Ignore>` is used to designate an attribute as ignored, which means it will be completely
ignored by the factory:

.. literalinclude:: /examples/fields/test_example_5.py
    :caption: Using the ``Ignore`` field
    :language: python

The ``Require`` Field
---------------------

The :class:`Require <polyfactory.fields.Require>` class is used to designate a given attribute as a required kwarg. This means that the
factory will require passing a value for this attribute as a kwarg to the build method, or an exception will be raised:

.. literalinclude:: /examples/fields/test_example_6.py
    :caption: Using the ``Require`` field
    :language: python

The ``PostGenerated`` Field
---------------------------

The :class:`PostGenerated <polyfactory.fields.PostGenerated>` class allows for post generating fields based on already generated
values of other (non post generated) fields. In most cases this pattern is best avoided, but for the few valid cases
the PostGenerated helper is provided. For example:

.. literalinclude:: /examples/fields/test_example_7.py
    :caption: Using the ``PostGenerated`` field
    :language: python

The signature for use is: ``cb: Callable, *args, **defaults``  it can receive any sync callable. The signature for the
callable should be: ``name: str, values: dict[str, Any], *args, **defaults``. The already generated values are mapped by
name in the values dictionary.


The ``Param`` Field
-------------------

The :class:`Param <polyfactory.fields.Param>` class denotes a constant parameter that can be referenced by other fields at build but is not mapped to the final object. This is useful for passing values needed by other factory fields but that are not part of object being built.

The Param type can either accept a constant value at the definition of the factory, or its value can be set at build time.

If neither a value is provided at the definition of the factory nor at build time, an exception will be raised.

.. literalinclude:: /examples/fields/test_example_9.py
    :caption: Using the ``Param`` field
    :language: python


The ``CallableParam`` Field
---------------------------

The :class:`CallableParam <polyfactory.fields.CallableParam>` class denotes a callable parameter with a return value that may be referenced by other fields during build but is not mapped to the final object. Optional keyword arguments may be passed to the callable as part of the field definition on the factory. Any additional keyword arguments passed to the build method will also not be passed to the final object.

The CallableParam type can either accept a callable provided at the definition of the factory, or its value can be passed at build time. The callable is executed at the beginning of build.

If neither a value is provided at the definition of the factory nor at build time, an exception will be raised.

The difference between a Param and a CallableParam is that the CallableParam is always executed at build time. If you need to pass an unmapped callable to the factory that should not automatically be executed at build time, use a Param.

.. literalinclude:: /examples/fields/test_example_10.py
    :caption: Using the ``CallableParam`` field
    :language: python

Factories as Fields
---------------------------

Factories themselves can be used as fields. In this usage, build parameters will be passed to the declared factory.

.. literalinclude:: /examples/fields/test_example_8.py
    :caption: Using a factory as a field
    :language: python
