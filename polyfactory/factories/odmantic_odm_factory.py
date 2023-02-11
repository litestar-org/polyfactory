from typing import TYPE_CHECKING, Any, Generic, Type, TypeVar

from polyfactory.exceptions import MissingExtensionDependency
from polyfactory.factories.pydantic_factory import ModelFactory
from polyfactory.fields import Ignore
from polyfactory.utils.predicates import is_safe_subclass

try:
    from odmantic import _BaseODMModel as OdmanticBaseModel  # type: ignore

except ImportError as e:
    raise MissingExtensionDependency("odmantic is not installed") from e

T = TypeVar("T", bound=OdmanticBaseModel)

if TYPE_CHECKING:
    from typing_extensions import TypeGuard


class OdmanticModelFactory(Generic[T], ModelFactory[T]):
    __is_base_factory__ = True

    @classmethod
    def is_supported_type(cls, value: Any) -> "TypeGuard[Type[T]]":
        return is_safe_subclass(value, OdmanticBaseModel)

    id = Ignore()
