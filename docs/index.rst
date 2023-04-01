Polyfactory
===========

.. note:: This project is under active overhaul and development.

Polyfactory is a simple and powerful mock data generation library using standard or third party data modeling libraries.


Installation
------------

.. code-block:: bash

    pip install polyfactory


Example
-------

.. note:: TODO: Update this example for Polyfactory

.. code-block:: python

    from datetime import date, datetime
    from typing import List, Union

    from pydantic import BaseModel, UUID4

    from pydantic_factories import ModelFactory


    class Person(BaseModel):
        id: UUID4
        name: str
        hobbies: List[str]
        age: Union[float, int]
        birthday: Union[datetime, date]


    class PersonFactory(ModelFactory):
        __model__ = Person


    result = PersonFactory.build()

That's it - with almost no work, we are able to create a mock data object fitting the Person class model definition.

This is possible because of the typing information available on the pydantic model and model-fields, which are used as a source of truth for data generation.

The factory parses the information stored in the pydantic model and generates a dictionary of kwargs that are passed to the Person class' init method.

.. toctree::
    :titlesonly:
    :caption: Documentation
    :hidden:

    usage/index
    reference/index
