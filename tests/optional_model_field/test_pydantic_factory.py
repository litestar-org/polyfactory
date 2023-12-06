from typing import Dict

from pydantic import BaseModel, Field
from typing_extensions import Annotated

from polyfactory.factories.pydantic_factory import ModelFactory


def test_mapping_with_annotated_item_types() -> None:
    ConstrainedInt = Annotated[int, Field(ge=100, le=200)]
    ConstrainedStr = Annotated[str, Field(min_length=1, max_length=3)]

    class Foo(BaseModel):
        dict_field: Dict[ConstrainedStr, ConstrainedInt]

    class FooFactory(ModelFactory[Foo]):
        ...

    assert getattr(FooFactory, "__model__") is Foo

    assert FooFactory.build()
