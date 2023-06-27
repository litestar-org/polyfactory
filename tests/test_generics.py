from typing import Generic, List, Optional, TypeVar, Union

from pydantic import BaseModel

from polyfactory.factories.pydantic_factory import ModelFactory

try:
    from pydantic.generics import GenericModel
except ImportError:
    GenericModel = BaseModel


Inner = TypeVar("Inner")
APIResponseData = TypeVar("APIResponseData")


class Attributes(GenericModel, Generic[Inner]):  # type: ignore
    attributes: Inner


class OneInner(BaseModel):
    one: str
    id: Optional[int]
    description: Optional[str]


class OneResponse(BaseModel):
    one: Attributes[OneInner]


class TwoInner(BaseModel):
    two: str
    id: Optional[int]
    description: Optional[str]


class TwoResponse(BaseModel):
    two: Attributes[TwoInner]


class ThreeInner(BaseModel):
    three: str
    relation: int


class ThreeResponse(BaseModel):
    three: Attributes[ThreeInner]


class APIResponse(GenericModel, Generic[APIResponseData]):  # type: ignore
    data: List[APIResponseData]


def test_generic_factory_one_response() -> None:
    class APIResponseFactory(ModelFactory[APIResponse[OneResponse]]):
        __model__ = APIResponse[OneResponse]

    result = APIResponseFactory.build()

    assert result.data
    assert isinstance(result.data[0], OneResponse)


def test_generic_factory_two_response() -> None:
    class APIResponseFactory(ModelFactory):
        __model__ = APIResponse[TwoResponse]

    result = APIResponseFactory.build()

    assert result.data
    assert isinstance(result.data[0], TwoResponse)


def test_generic_factory_three_response() -> None:
    class APIResponseFactory(ModelFactory):
        __model__ = APIResponse[ThreeResponse]

    result = APIResponseFactory.build()

    assert result.data
    assert isinstance(result.data[0], ThreeResponse)


def test_generic_factory_union_response() -> None:
    class APIResponseFactory(ModelFactory):
        __model__ = APIResponse[Union[OneResponse, TwoResponse, ThreeResponse]]

    result = APIResponseFactory.build()

    assert result.data
    assert isinstance(result.data[0], (OneResponse, TwoResponse, ThreeResponse))
