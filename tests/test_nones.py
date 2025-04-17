from typing import Optional

from pydantic import BaseModel

from polyfactory.factories.pydantic_factory import ModelFactory
from polyfactory.fields import AlwaysNone, NeverNone


def test_never_none() -> None:
    class MyModel(BaseModel):
        name: Optional[str]

    class MyFactory(ModelFactory[MyModel]):
        name = NeverNone()

    assert MyFactory.build().name is not None


def test_always_none() -> None:
    class MyModel(BaseModel):
        name: Optional[str]

    class MyFactory(ModelFactory[MyModel]):
        name = AlwaysNone()
        # NOTE `name = None` does not end up

    # field is still accessible even though there is
    assert MyFactory.build().name is None
