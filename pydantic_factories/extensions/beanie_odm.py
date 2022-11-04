from typing import TYPE_CHECKING, Any, List, Union

from pydantic import BaseModel

from pydantic_factories.factory import ModelFactory
from pydantic_factories.protocols import AsyncPersistenceProtocol

try:
    from beanie import Document
except ImportError:
    Document = BaseModel  # type: ignore

if TYPE_CHECKING:
    from pydantic.fields import ModelField


class BeaniePersistenceHandler(AsyncPersistenceProtocol[Document]):
    async def save(self, data: Document) -> Document:
        """Persists a single instance in mongoDB."""
        return await data.insert()  # type: ignore

    async def save_many(self, data: List[Document]) -> List[Document]:
        """Persists multiple instances in mongoDB.

        Note: we cannot use the .insert_many method from Beanie here because it doesn't return the created instances
        """
        result = []
        for doc in data:
            result.append(await doc.insert())
        return result


class BeanieDocumentFactory(ModelFactory[Document]):
    """Subclass of ModelFactory for Beanie Documents."""

    __async_persistence__ = BeaniePersistenceHandler

    @classmethod
    def get_field_value(cls, model_field: "ModelField", field_parameters: Union[dict, list, None] = None) -> Any:
        """Override to handle the fields created by the beanie Indexed helper
        function.

        Note: these fields do not have a class we can use, rather they instantiate a private class inside a closure.
        Hence, the hacky solution of checking the __name__ property
        """
        if hasattr(model_field.type_, "__name__") and "Indexed " in model_field.type_.__name__:
            base_type = model_field.outer_type_.__bases__[0]
            model_field.outer_type_ = base_type
            model_field.type_ = base_type

        if hasattr(model_field.type_, "__name__") and "Link" in model_field.type_.__name__:
            link_class = model_field.outer_type_.__args__[0]
            model_field.outer_type_ = link_class
            model_field.type_ = link_class

        return super().get_field_value(model_field=model_field, field_parameters=field_parameters)
