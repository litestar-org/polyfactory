The ``post_generated`` decorator
--------------------------------

The :class:`post_generated <polyfactory.decorators.post_generated>` decorator wraps a ``classmethod`` into a
:class:`PostGenerated <polyfactory.fields.PostGenerated>` field. This is useful when the post generated field depends
on the current factory, usually its ``__faker__`` and/or ``__random__`` attribute. For example:

.. literalinclude:: /examples/decorators/test_example_1.py
    :caption: Using the ``post_generated`` decorator
    :language: python

All classmethod parameters after ``cls`` must be named as the fields this post generated field depends on.
