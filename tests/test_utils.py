from typing import Any, Union

from pydantic import BaseModel

from pydantic_factories.factory import ModelFactory
from pydantic_factories.utils import is_union


def test_is_union():
    class UnionPipe(BaseModel):
        union_pipe: int | str  # Pipe syntax supported from Python 3.10 onwards
        union_normal: Union[int, str]
        no_union: Any

    class UnionPipeFactory(ModelFactory):
        __model__ = UnionPipe

    for field_name, model_field in UnionPipeFactory.get_model_fields(UnionPipeFactory._get_model()):
        if (field_name == "union_pipe") or (field_name == "union_normal"):
            assert is_union(model_field)
        else:
            assert not is_union(model_field)
