from typing import TYPE_CHECKING, Any, Generic, Type, TypeVar, Union

from polyfactory.exceptions import MissingDependencyException
from polyfactory.factories.pydantic_factory import ModelFactory
from polyfactory.fields import Ignore
from polyfactory.utils.predicates import is_safe_subclass

try:
    from odmantic import EmbeddedModel, Model

except ImportError as e:
    raise MissingDependencyException("odmantic is not installed") from e

T = TypeVar("T", bound=Union[Model, EmbeddedModel])

if TYPE_CHECKING:
    from typing_extensions import TypeGuard


class OdmanticModelFactory(Generic[T], ModelFactory[T]):
    __is_base_factory__ = True

    @classmethod
    def is_supported_type(cls, value: Any) -> "TypeGuard[Type[T]]":
        return is_safe_subclass(value, Model) or is_safe_subclass(value, EmbeddedModel)

    id = Ignore()
