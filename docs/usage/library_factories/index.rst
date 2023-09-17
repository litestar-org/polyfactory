Polyfactory Factories
=====================

The factories exported by this library are classes that extend the
Abstract Base Class (ABC) :class:`BaseFactory <polyfactory.factories.base.BaseFactory>`.

These include:

:class:`DataclassFactory <polyfactory.factories.dataclass_factory.DataclassFactory>`
    a base factory for dataclasses

:class:`TypedDictFactory <polyfactory.factories.typed_dict_factory.TypedDictFactory>`
    a base factory for typed-dicts
:class:`ModelFactory <polyfactory.factories.pydantic_factory.ModelFactory>`
    a base factory for `pydantic <https://docs.pydantic.dev/>`_ models

:class:`BeanieDocumentFactory <polyfactory.factories.beanie_odm_factory.BeanieDocumentFactory>`
    a base factory for `beanie <https://beanie-odm.dev/>`_ documents

:class:`OdmanticModelFactory <polyfactory.factories.odmantic_odm_factory.OdmanticModelFactory>`
    a base factory for `odmantic <https://art049.github.io/odmantic/>`_ models.

:class:`MsgspecFactory <polyfactory.factories.msgspec_factory.MsgspecFactory>`
    a base factory for `msgspec <https://jcristharif.com/msgspec/>`_ Structs

:class:`AttrsFactory <polyfactory.factories.attrs_factory.AttrsFactory>`
    a base factory for `attrs <https://www.attrs.org/en/stable/index.html>`_ models.

:class:`SQLAlchemyFactory <polyfactory.factories.sqlalchemy_factory.SQLAlchemyFactory>`
    a base factory for `SQLAlchemy <https://www.sqlalchemy.org/>`_ models.

.. note::
    All factories exported from ``polyfactory.factories`` do not require any additional dependencies. The other factories,
    such as :class:`ModelFactory <polyfactory.factories.pydantic_factory.ModelFactory>`, require an additional but optional
    dependency, in this case `pydantic <https://docs.pydantic.dev/>`_. As such, they are exported only from their respective
    namespaced module, e.g. ``polyfactory.factories.pydantic_factory.ModelFactory``.

.. note::
    We will be adding additional factories to this package, so make sure to checkout the above list from time to time.


.. toctree::
    :maxdepth: 1

    sqlalchemy_factory
