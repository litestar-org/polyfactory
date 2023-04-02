from __future__ import annotations
from typing import TYPE_CHECKING, Any, Generic, TypeVar, Union

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
    """Base factory for odmantic models"""

    __is_base_factory__ = True

    @classmethod
    def is_supported_type(cls, value: Any) -> "TypeGuard[type[T]]":
        """Determine whether the given value is supported by the factory.

        :param value: An arbitrary value.
        :returns: A typeguard
        """
        return is_safe_subclass(value, Model) or is_safe_subclass(value, EmbeddedModel)

    id = Ignore()
