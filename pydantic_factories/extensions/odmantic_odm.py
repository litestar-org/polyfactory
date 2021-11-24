from typing import TypeVar

from pydantic import BaseModel

from pydantic_factories.factory import ModelFactory
from pydantic_factories.fields import Ignore

try:
    from odmantic import EmbeddedModel, Model
except ImportError:  # pragma: no cover
    Model = BaseModel
    EmbeddedModel = BaseModel


T = TypeVar("T", Model, EmbeddedModel)


class OdmanticModelFactory(ModelFactory[T]):
    id = Ignore()
