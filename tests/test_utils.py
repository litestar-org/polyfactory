import sys
from typing import Any, Union

from pydantic import BaseModel

from pydantic_factories.factory import ModelFactory
from pydantic_factories.utils import is_union


def test_is_union() -> None:
    class UnionTest(BaseModel):
        union: Union[int, str]
        no_union: Any

    class UnionTestFactory(ModelFactory):
        __model__ = UnionTest

    for field_name, model_field in UnionTestFactory.get_model_fields(UnionTestFactory._get_model()):
        if field_name == "union":
            assert is_union(model_field)
        else:
            assert not is_union(model_field)

    # for python 3.10 we need to run the test as well with the union_pipe operator
    if sys.version_info >= (3, 10):

        class UnionTestWithPipe(BaseModel):
            union_pipe: int | str | None  # Pipe syntax supported from Python 3.10 onwards
            union_normal: Union[int, str]
            no_union: Any

        class UnionTestWithPipeFactory(ModelFactory):
            __model__ = UnionTestWithPipe

        for field_name, model_field in UnionTestWithPipeFactory.get_model_fields(UnionTestWithPipeFactory._get_model()):
            if field_name in ("union_pipe", "union_normal"):
                assert is_union(model_field)
            else:
                assert not is_union(model_field)
