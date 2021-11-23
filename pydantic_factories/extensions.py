from typing import Any, List, TypeVar

from pydantic import BaseModel
from pydantic.fields import ModelField

from pydantic_factories import AsyncPersistenceProtocol
from pydantic_factories.factory import ModelFactory

try:
    from beanie import Document
    from beanie.odm.fields import PydanticObjectId
except ImportError:  # pragma: no cover
    PydanticObjectId = None
    Document = BaseModel

T = TypeVar("T", bound=Document)


class BeaniePersistenceHandler(AsyncPersistenceProtocol[T]):
    async def save(self, data: T) -> T:
        """
        Persists a single instance in mongoDB
        """
        return await data.insert()

    async def save_many(self, data: List[T]) -> List[T]:
        """
        Persists multiple instances in mongoDB

        Note: we cannot use the .insert_many method from Beanie here because it doesn't return the created instances
        """
        result = []
        for doc in data:
            result.append(await doc.insert())
        return result


class BeanieDocumentFactory(ModelFactory[T]):
    """Subclass of ModelFactory for Beanie Documents"""

    __async_persistence__ = BeaniePersistenceHandler

    @classmethod
    def is_ignored_type(cls, value: Any) -> bool:
        """
        Overriden to exclude PydanticObjectId

        """
        return value is None or value is PydanticObjectId

    @classmethod
    def get_field_value(cls, field_name: str, model_field: ModelField) -> Any:
        """
        Override to handle the fields created by the beanie Indexed helper function

        Note: these fields do not have a class we can use, rather they instantiate a private class inside a closure.
        Hence the hacky solution of checking the __name__ property
        """
        if hasattr(model_field.type_, "__name__") and "Indexed " in model_field.type_.__name__:
            base_type = model_field.outer_type_.__bases__[0]
            model_field.outer_type_ = base_type
            model_field.type_ = base_type
        return super().get_field_value(field_name=field_name, model_field=model_field)
