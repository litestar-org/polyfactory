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

That's it - with almost no work, we are able to create a mock data object fitting the Person class model definition.

This is possible because of the typing information available on the pydantic model and model-fields, which are used as a source of truth for data generation.

The factory parses the information stored in the pydantic model and generates a dictionary of kwargs that are passed to the Person class' init method.

.. toctree::
    :titlesonly:
    :caption: Documentation
    :hidden:

    usage/index
    reference/index
