from typing import Any, Union

from pydantic import BaseModel

from pydantic_factories.factory import ModelFactory
from pydantic_factories.utils import is_union


def test_is_union():
    class UnionTest(BaseModel):
        union_pipe: int | str | None  # Pipe syntax supported from Python 3.10 onwards
        union_normal: Union[int, str]
        no_union: Any

    class UnionTestFactory(ModelFactory):
        __model__ = UnionTest

    for field_name, model_field in UnionTestFactory.get_model_fields(UnionTestFactory._get_model()):
        if (field_name == "union_pipe") or (field_name == "union_normal"):
            assert is_union(model_field)
        else:
            assert not is_union(model_field)
