from typing import TypeVar

from pydantic import BaseModel

from pydantic_factories.factory import ModelFactory
from pydantic_factories.fields import Ignore

try:  # pragma: no cover
    from odmantic import EmbeddedModel, Model
except ImportError:  # pragma: no cover
    Model = BaseModel
    EmbeddedModel = BaseModel


T = TypeVar("T", Model, EmbeddedModel)

# FIX: once odmantic updates to pydantic 1.9.0, uncomment the tests and return this to the dev dependencies


class OdmanticModelFactory(ModelFactory[T]):  # pragma: no cover
    id = Ignore()
