Polyfactory
===========

Polyfactory is a simple and powerful mock data generation library, based around type
hints and supporting dataclasses, typed-dicts, pydantic models, msgspec structs and more.

Installation
------------

.. code-block:: bash

    pip install polyfactory


Relation to Pydantic-Factories
------------------------------

Prior to version 2, this library was known as `pydantic-factories <https://pypi.org/project/pydantic-factories/>`_, a
name under which it gained quite a bit of popularity.

A main motivator for the 2.0 release was that we wanted to support more than just Pydantic models, something which also
required a change to its core architecture. As this library would no longer be directly tied to Pydantic, `polyfactory`
was chosen as its new name to reflect its capabilities; It can generate mock data for dataclasses, typed-dicts,
Pydantic, odmantic, and beanie ODM models, as well as custom factories.

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

.. toctree::
    :titlesonly:
    :caption: Development
    :hidden:

    contributing
