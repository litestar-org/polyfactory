Declaring Factories
===================

Defining factories is done using a declarative syntax. That is - users declare factory classes, which are subclasses of
base factories.

.. literalinclude:: /examples/declaring_factories/test_example_1.py
    :caption: Declaring a factory for a dataclass
    :language: python

.. note::
    .. |white_check_mark|  unicode:: U+2705
    .. |cross_mark|  unicode:: U+274C
    .. |warning|  unicode:: U+26A0

    Let's have a closer look at the factory declaration.
    There are two places where the model type is provided:
    ``__model__`` class attribute and generic type parameter.

    .. list-table::
       :align: left
       :width: 60%
       :header-rows: 1

       * - Place
         - Purpose
       * - ``__model__ = Person``
         - Model mock-data generation (core feature)
       * - ``DataclassFactory[Person]``
         - Type hints (optional)

    In previous library version you had to specify both ``__model__`` class attribute
    and generic type parameter to get core and type hints features.

    .. list-table::
       :align: left
       :width: 100%
       :header-rows: 1

       * -
         - |white_check_mark| ``DataclassFactory[Person]``
         - |cross_mark| ``DataclassFactory``
       * - |white_check_mark| ``__model__ = Person``
         - |white_check_mark| OK
         - |warning| OK (no type hints)
       * - |cross_mark| ``__model__`` omitting
         - |cross_mark| Error
         - |cross_mark| Error

    Now you can omit ``__model__`` attribute assigning.

    .. list-table::
       :width: 100%
       :header-rows: 1

       * -
         - |white_check_mark| ``DataclassFactory[Person]``
         - |cross_mark| ``DataclassFactory``
       * - |white_check_mark| ``__model__ = Person``
         - |white_check_mark| OK (``__model__`` priority)
         - |warning| OK (no type hints)
       * - |cross_mark| ``__model__`` omitting
         - |white_check_mark| OK (infer from generic type)
         - |cross_mark| Error

    So the syntax is

    .. code-block:: python

        class PersonFactory(DataclassFactory[Person]):
            ...

    If you specify different types in both places -- that doesn't make any sense --
    the ``__model__`` class attribute type will be used over generic parameter type.


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
