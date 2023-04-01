Defining Factories
==================

Defining factories is done using a declarative syntax. That is - users declare factory classes, which are subclasses of
base factories.

.. literalinclude:: /examples/defining_factories/test_example_1.py
    :caption: Declaring a factory for a dataclass
    :language: python

The same applies to the other factories exported by this library, for example:

.. literalinclude:: /examples/defining_factories/test_example_2.py
    :caption: Declaring a factory for a typed-dict
    :language: python

Or for pydantic models:

.. literalinclude:: /examples/defining_factories/test_example_3.py
    :caption: Declaring a factory for a pydantic model
    :language: python

.. note::
    You can also define factories for any 3rd party implementation of dataclasses, as long as it fulfills the stdlib
    dataclasses interface. For example, this is using the pydantic ``@dataclass`` decorator:

    .. literalinclude:: /examples/defining_factories/test_example_4.py
        :caption: Declaring a factory for a pydantic dataclass
        :language: python
