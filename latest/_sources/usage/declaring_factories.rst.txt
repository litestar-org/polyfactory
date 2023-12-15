Declaring Factories
===================

Defining factories is done using a declarative syntax. That is - users declare factory classes, which are subclasses of
base factories.

.. literalinclude:: /examples/declaring_factories/test_example_1.py
    :caption: Declaring a factory for a dataclass
    :language: python

You can also specify the model type by only specifying the factory generic type parameter.

.. code-block:: python

    @dataclass
    class Person:
        name: str
        age: float
        height: float
        weight: float

    class PersonFactory(DataclassFactory[Person]):
        ...

.. note::
   The syntax with the ``__model__`` class attribute omitting
   is only available since version 2.13.0.

The same applies to the other factories exported by this library, for example:

.. literalinclude:: /examples/declaring_factories/test_example_2.py
    :caption: Declaring a factory for a typed-dict
    :language: python

Or for pydantic models:

.. literalinclude:: /examples/declaring_factories/test_example_3.py
    :caption: Declaring a factory for a pydantic model
    :language: python

.. note::
    You can also define factories for any 3rd party implementation of dataclasses, as long as it fulfills the stdlib
    dataclasses interface. For example, this is using the pydantic ``@dataclass`` decorator:

    .. literalinclude:: /examples/declaring_factories/test_example_4.py
        :caption: Declaring a factory for a pydantic dataclass
        :language: python

Or for attrs models:

.. literalinclude:: /examples/declaring_factories/test_example_7.py
    :caption: Declaring a factory for a attrs model
    :language: python

.. note::
    Validators are not currently supported - neither the built in validators that come
    with `attrs` nor custom validators.


Imperative Factory Creation
---------------------------

Although the definition of factories is primarily meant to be done imperatively, factories expose the
:meth:`create_factory <polyfactory.factories.base.BaseFactory.create_factory>` method. This method is used internally
inside factories to dynamically create factories for models. For example, below the ``PersonFactory`` will dynamically
create a ``PetFactory``:

.. literalinclude:: /examples/declaring_factories/test_example_5.py
    :caption: Dynamic factory generation
    :language: python

You can also use this method to create factories imperatively:

.. literalinclude:: /examples/declaring_factories/test_example_6.py
    :caption: Imperative factory creation
    :language: python

Eventually you can use this method on an existing concrete factory to create a sub factory overriding some parent configuration:

.. literalinclude:: /examples/declaring_factories/test_example_8.py
    :caption: Imperative sub factory creation
    :language: python

In this case you don't need to specify the `model` argument to the :meth:`create_factory <polyfactory.factories.base.BaseFactory.create_factory>` method. The one from the parent factory will be used.
