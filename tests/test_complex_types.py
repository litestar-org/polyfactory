from dataclasses import dataclass
from enum import Enum
from typing import (
    Any,
    Callable,
    DefaultDict,
    Deque,
    Dict,
    FrozenSet,
    Generic,
    Iterable,
    List,
    Literal,
    Optional,
    Sequence,
    Set,
    Tuple,
    TypeVar,
    Union,
)

import pytest

from pydantic import BaseModel

from polyfactory.exceptions import ParameterException
from polyfactory.factories import DataclassFactory
from polyfactory.factories.pydantic_factory import ModelFactory
from tests.models import Person


def test_handles_complex_typing() -> None:
    class MyModel(BaseModel):
        nested_dict: Dict[str, Dict[Union[int, str], Dict[Any, List[Dict[str, str]]]]]
        dict_str_any: Dict[str, Any]
        nested_list: List[List[List[Dict[str, List[Any]]]]]
        sequence_literal: Sequence[Literal[1, 2, 3]]
        sequence_dict: Sequence[Dict[str, Any]]
        iterable_float: Iterable[float]
        tuple_ellipsis: Tuple[int, ...]
        tuple_str_str: Tuple[str, str]
        default_dict: DefaultDict[str, List[Dict[str, int]]]
        deque: Deque[List[Dict[str, int]]]
        set_union: Set[Union[str, int]]
        frozen_set: FrozenSet[str]
        plain_list: List[Any]
        plain_set: Set[Any]
        plain_dict: Dict[str, Any]

    class MyFactory(ModelFactory):
        __model__ = MyModel

    result = MyFactory.build()
    assert result.nested_dict
    assert result.dict_str_any
    assert result.nested_list
    assert result.sequence_dict
    assert result.iterable_float
    assert result.tuple_ellipsis
    assert result.tuple_str_str
    assert result.default_dict
    assert result.deque
    assert result.set_union
    assert result.frozen_set
    assert result.plain_list
    assert result.plain_set
    assert result.plain_dict


def test_handles_complex_typing_with_embedded_models() -> None:
    class MyModel(BaseModel):
        person_dict: Dict[str, Person]
        person_list: List[Person]

    class MyFactory(ModelFactory):
        __model__ = MyModel

    result = MyFactory.build()

    assert result.person_dict
    assert result.person_list[0].pets


def test_raises_for_user_defined_types() -> None:
    class MyClass:
        def __init__(self, value: int) -> None:
            self.value = value

    class MyModel(BaseModel):
        my_class_field: Dict[str, MyClass]

        class Config:
            arbitrary_types_allowed = True

    class MyFactory(ModelFactory):
        __model__ = MyModel

    with pytest.raises(ParameterException):
        MyFactory.build()


def test_randomizes_optional_returns() -> None:
    """this is a flaky test - because it depends on randomness, hence it's been re-ran multiple times."""

    class MyModel(BaseModel):
        optional_1: Optional[List[str]]
        optional_2: Optional[Dict[str, str]]
        optional_3: Optional[Set[str]]
        optional_4: Optional[Dict[int, str]]

    class MyFactory(ModelFactory):
        __model__ = MyModel
        __random_seed__ = 1

    failed = False
    for _ in range(5):
        try:
            result = MyFactory.build()
            assert any(
                [
                    not result.optional_1,
                    not result.optional_2,
                    not result.optional_3,
                    not result.optional_4,
                ],
            )
            assert any(
                [
                    bool(result.optional_1),
                    bool(result.optional_2),
                    bool(result.optional_3),
                    bool(result.optional_4),
                ],
            )
            failed = False
            break
        except AssertionError:
            failed = True
    assert not failed


def test_complex_typing_with_enum() -> None:
    class Animal(str, Enum):
        DOG = "Dog"
        CAT = "Cat"
        MONKEY = "Monkey"

    class MyModel(BaseModel):
        animal_list: List[Animal]

    class MyFactory(ModelFactory):
        __model__ = MyModel

    result = MyFactory.build()
    assert result.animal_list


def test_union_literal() -> None:
    class MyModel(BaseModel):
        x: Union[int, Literal["a", "b", "c"]]

    class MyFactory(ModelFactory):
        __model__ = MyModel

    MyFactory.build()


def test_non_collection_generic() -> None:
    T = TypeVar("T")

    class LoggedVar(Generic[T]):
        def __init__(self, name: str = "", log: Callable[[str], None] = print) -> None:
            self.__name = name
            self.__log = log

        def set(self, value: T) -> None:
            self.__log(f"Set {self.__name} to {value}")
            self.__value = value

        def get(self) -> T:
            self.__log(f"Get {self.__name} = {self.__value}")
            return self.__value

    @dataclass
    class MyModel:
        x: LoggedVar[int]

    class MyFactory(DataclassFactory):
        __model__ = MyModel

    result = MyFactory.build()
    assert isinstance(result.x, LoggedVar)


def test_sequence_dict() -> None:
    @dataclass
    class MyModel:
        sequence_dict: Sequence[Dict]

    class MyFactory(DataclassFactory):
        __model__ = MyModel

    result = MyFactory.build()

    assert result.sequence_dict
