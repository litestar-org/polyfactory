from typing import (
    Any,
    DefaultDict,
    Deque,
    Dict,
    FrozenSet,
    Iterable,
    List,
    Mapping,
    Optional,
    Sequence,
    Set,
    Tuple,
    Union,
)

import pytest
from pydantic import BaseModel

from pydantic_factories import ModelFactory
from pydantic_factories.exceptions import ParameterError
from tests.models import Person


def test_handles_complex_typing():
    class MyModel(BaseModel):
        nested_dict: Dict[str, Dict[Union[int, str], Dict[Any, List[Dict[str, str]]]]]
        dict_str_any: Dict[str, Any]
        nested_list: List[List[List[Dict[str, List[Any]]]]]
        sequence_dict: Sequence[Dict]
        iterable_float: Iterable[float]
        tuple_ellipsis: Tuple[int, ...]
        tuple_str_str: Tuple[str, str]
        default_dict: DefaultDict[str, List[Dict[str, int]]]
        deque: Deque[List[Dict[str, int]]]
        set_union: Set[Union[str, int]]
        frozen_set: FrozenSet[str]

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


def test_handles_complex_typing_with_embedded_models():
    class MyModel(BaseModel):
        person_dict: Dict[str, Person]
        person_list: List[Person]

    class MyFactory(ModelFactory):
        __model__ = MyModel

    result = MyFactory.build()

    assert result.person_dict
    assert result.person_list[0].pets


def test_raises_for_user_defined_types():
    class MyClass:
        pass

    class MyModel(BaseModel):
        my_class_field: Dict[str, MyClass]

        class Config:
            arbitrary_types_allowed = True

    class MyFactory(ModelFactory):
        __model__ = MyModel

    with pytest.raises(ParameterError):
        MyFactory.build()


def test_randomizes_optional_returns():
    """this is a flaky test - because it depends on randomness, hence its been reran multiple times."""

    class MyModel(BaseModel):
        optional_1: List[Optional[str]]
        optional_2: Dict[str, Optional[str]]
        optional_3: Set[Optional[str]]
        optional_4: Mapping[int, Optional[str]]

    class MyFactory(ModelFactory):
        __model__ = MyModel

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
                ]
            )
            assert any(
                [
                    bool(result.optional_1),
                    bool(result.optional_2),
                    bool(result.optional_3),
                    bool(result.optional_4),
                ]
            )
            failed = False
            break
        except AssertionError:
            failed = True
    assert not failed
