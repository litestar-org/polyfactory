Factory Fields
==============

The factory api is designed to be as semantic and simple as possible, and by default it requires no customization to
mock data. Nonetheless, when you do need to customize and control the data being generated, polyfactory has you covered.
Lets look at a few examples:

.. literalinclude:: /examples/factory_fields/test_example_1.py
    :caption: Declaring a PersonFactory with preset pets
    :language: python

In the example above, the call to ``PersonFactory.build()`` results in a ``Person`` where all values are randomly
generated, except the ``pets`` list, which will be the hardcoded value we defined.

The ``Use`` Field
-----------------

This though is often not desirable. We could instead, define a factory for Pet where we restrict the choices to a range
we like. For example:

.. literalinclude:: /examples/factory_fields/test_example_1.py
    :caption: Using the ``Use`` field with a custom PetFactory to control the generation of a Person's pets list.
    :language: python

The :class:`Use <polyfactory.Use>` class is merely a semantic abstraction that makes the factory cleaner and simpler
to understand, you can in fact use any callable (including classes) as values for a factory's attribute directly, and
these will be invoked at build-time. Thus, you could for example re-write the above PetFactory like so:

.. code-block:: python
    class PetFactory(DataclassFactory[Pet]):
    __model__ = Pet

    name = lambda: DataclassFactory.__random__.choice(["Ralph", "Roxy"])
    species = lambda: DataclassFactory.__random__.choice(list(Species))

Or you can use a class method, which will give you easy and nice access to the factory itself:

.. code-block:: python
    class PetFactory(DataclassFactory[Pet]):
    __model__ = Pet

    @classmethod
    def name() -> str:
        return cls.__random__.choice(["Ralph", "Roxy"])

    @classmethod
    def species() -> str:
        return cls.__random__.choice(list(Species))

.. note::
    All the above examples used ``DataclassFactory.__random__.choice``, and this is intentional. While you can use
    ``random.choice`` or any other function exported from the stdlib random library, the factory class has its own instance
    of ``random.Random`` attached under ``cls.__random__``. This instance can be affected by random seeding in several ways, e.g.
    calling the factory seeding method, which will be scoped only to this instance. Thus, for consistent results when seeding
    randomness, its important to use the factory ``random.Random`` instance rather than the global one from the stdlib.
