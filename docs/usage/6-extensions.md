# Extensions

Any class that is derived from pydantic's `BaseModel` can be used as the `__model__` of a factory. For most 3rd party
libraries, e.g. [SQLModel](https://sqlmodel.tiangolo.com/), this library will work as is out of the box.

Currently, this library also includes the following extensions:

## ODMantic

This extension includes a class called `OdmanticModelFactory` and it can be imported from `pydantic_factory.extensions`.
This class is meant to be used with the `Model` and `EmbeddedModel` classes exported by ODMantic, but it will also work
with regular instances of pydantic's `BaseModel`.

## Beanie

This extension includes a class called `BeanieDocumentFactory` as well as an `BeaniePersistenceHandler`. Both of these
can be imported from `pydantic_factory.extensions`. The `BeanieDocumentFactory` is meant to be used with the
Beanie `Document` class, and it includes async persistence build in.
