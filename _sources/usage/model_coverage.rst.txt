Model coverage generation
=========================

The ``BaseFactory.coverage()`` function is an alternative approach to ``BaseFactory.batch()``, where the examples that are generated attempt to provide full coverage of all the forms a model can take with the minimum number of instances. For example:

.. literalinclude:: /examples/model_coverage/test_example_1.py
    :caption: Defining a factory and generating examples with coverage
    :language: python

As you can see in the above example, the ``Profile`` model has 3 options for ``favourite_color``, and 2 options for ``vehicle``. In the output you can expect to see instances of ``Profile`` that have each of these options. The largest variance dictates the length of the output, in this case ``favourite_color`` has the most, at 3 options, so expect to see 3 ``Profile`` instances.


.. note::
    Notice that the same ``Car`` instance is used in the first and final generated example. When the coverage examples for a field are exhausted before another field, values for that field are re-used.

Notes on collection types
-------------------------

When generating coverage for models with fields that are collections, in particular collections that contain sub-models, the contents of the collection will be the all coverage examples for that sub-model. For example:

.. literalinclude:: /examples/model_coverage/test_example_2.py
    :caption: Coverage output for the SocialGroup model
    :language: python

Known Limitations
-----------------

- Recursive models will cause an error: ``RecursionError: maximum recursion depth exceeded``.
- ``__min_collection_length__`` and ``__max_collection_length__`` are currently ignored in coverage generation.
