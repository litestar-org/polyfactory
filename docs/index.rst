Polyfactory
===========

Polyfactory is a simple and powerful mock data generation library.

Installation
------------

.. code-block:: bash

    pip install polyfactory


Relation to Pydantic-Factories
------------------------------

The earlier version of this library was released under the name [pydantic-factories](https://pypi.org/project/pydantic-factories/).
While this library became very popular (above 100K monthly downloads), we decided to rename it because we changed the core architecture -
`polyfactory` is a fitting name because we no longer rely on pydantic, which is now an optional dependency. This library is capable of
generating mock data for dataclasses, typed-dicts and any custom factory using type annotations.
It also supports using pydantic models - but that is optional.


Example
-------

.. literalinclude:: /examples/declaring_factories/test_example_1.py
    :caption: Minimal example using a dataclass
    :language: python

That's it - with almost no work, we are able to create a mock data object fitting the Person class model definition.

This is possible because of the typing information available on the dataclass, which are used as a
source of truth for data generation.

The factory parses the information stored in the dataclass and generates a dictionary of kwargs that are passed to
the Person class constructor.

.. toctree::
    :titlesonly:
    :caption: Documentation
    :hidden:

    usage/index
    reference/index
