import sys
from datetime import date
from decimal import Decimal
from types import ModuleType
from typing import Any, Callable, Dict, List, NewType, Optional, Tuple, Union

import pytest

from pydantic import (
    VERSION,
    BaseModel,
    PositiveFloat,
    conbytes,
    condate,
    condecimal,
    confloat,
    confrozenset,
    conint,
    conlist,
    conset,
    constr,
)

from polyfactory.factories.dataclass_factory import DataclassFactory
from polyfactory.factories.pydantic_factory import ModelFactory


def test_new_types() -> None:
    MyInt = NewType("MyInt", int)
    WrappedInt = NewType("WrappedInt", MyInt)

    class MyModel(BaseModel):
        int_field: MyInt
        wrapped_int_field: WrappedInt

    class MyModelFactory(ModelFactory):
        __model__ = MyModel

    result = MyModelFactory.build()
    assert isinstance(result.int_field, int)
    assert isinstance(result.wrapped_int_field, int)


def test_complex_new_types() -> None:
    MyStr = NewType("MyStr", str)
    MyInt = NewType("MyInt", int)

    class NestedModel(BaseModel):
        nested_int_field: MyInt

    MyNestedModel = NewType("MyNestedModel", NestedModel)

    class MyModel(BaseModel):
        list_int_field: List[MyInt]
        union_field: Union[MyInt, MyStr]
        optional_str_field: Optional[MyStr]
        tuple_str_str: Tuple[MyStr, MyStr]
        dict_field: Dict[MyStr, Any]
        complex_dict_field: Dict[MyStr, Dict[Union[MyInt, MyStr], MyInt]]
        nested_model_field: MyNestedModel

    class MyModelFactory(ModelFactory):
        __model__ = MyModel

    result = MyModelFactory.build()

    assert isinstance(result.list_int_field[0], int)
    assert isinstance(result.union_field, (int, str))
    assert result.optional_str_field is None or isinstance(result.optional_str_field, str)
    assert isinstance(result.tuple_str_str, tuple)
    assert isinstance(result.dict_field, dict)
    assert isinstance(result.nested_model_field, NestedModel)
    assert isinstance(result.nested_model_field.nested_int_field, int)


@pytest.mark.skipif(VERSION.startswith("2"), reason="https://github.com/pydantic/pydantic/issues/5907")
def test_constrained_new_types() -> None:
    ConBytes = NewType("ConBytes", conbytes(min_length=2, max_length=4))  # type: ignore[misc]
    ConStr = NewType("ConStr", constr(min_length=10, max_length=15))  # type: ignore[misc]
    ConInt = NewType("ConInt", conint(gt=100, lt=110))  # type: ignore[misc]
    ConFloat = NewType("ConFloat", confloat(lt=-100))  # type: ignore[misc]
    ConDecimal = NewType("ConDecimal", condecimal(ge=Decimal(6), le=Decimal(8)))  # type: ignore[misc]
    ConDate = NewType("ConDate", condate(gt=date.today()))  # type: ignore[misc]
    ConMyPositiveFloat = NewType("ConMyPositiveFloat", PositiveFloat)

    if VERSION.startswith("1"):
        ConList = NewType("ConList", conlist(item_type=int, min_items=3))  # type: ignore
        ConSet = NewType("ConSet", conset(item_type=int, min_items=4))  # type: ignore
        ConFrozenSet = NewType("ConFrozenSet", confrozenset(item_type=str, min_items=5))  # type: ignore
    else:
        ConList = NewType("ConList", conlist(item_type=int, min_length=3))  # type: ignore
        ConSet = NewType("ConSet", conset(item_type=int, min_length=4))  # type: ignore
        ConFrozenSet = NewType("ConFrozenSet", confrozenset(item_type=str, min_length=5))  # type: ignore

    class ConstrainedModel(BaseModel):
        conbytes_field: ConBytes
        constr_field: ConStr
        conint_field: ConInt
        confloat_field: ConFloat
        condecimal_field: ConDecimal
        condate_field: ConDate
        conlist_field: ConList
        conset_field: ConSet
        confrozenset_field: ConFrozenSet
        conpositive_float_field: ConMyPositiveFloat

    class MyFactory(ModelFactory):
        __model__ = ConstrainedModel

    result = MyFactory.build()

    # we want to make sure that NewType is correctly unwrapped retaining
    # original type and its attributes. More elaborate testing of constrained
    # fields is done in tests/constraints/
    assert isinstance(result.conbytes_field, bytes)
    assert 2 <= len(result.conbytes_field) <= 4

    assert isinstance(result.constr_field, str)
    assert 10 <= len(result.constr_field) <= 15

    assert isinstance(result.conint_field, int)
    assert 100 < result.conint_field < 110

    assert isinstance(result.confloat_field, float)
    assert result.confloat_field < -100

    assert isinstance(result.condecimal_field, Decimal)
    assert Decimal(6) <= result.condecimal_field <= Decimal(8)

    assert isinstance(result.condate_field, date)
    assert result.condate_field > date.today()

    assert isinstance(result.conlist_field, list)
    assert len(result.conlist_field) >= 3

    assert isinstance(result.conset_field, set)
    assert len(result.conset_field) >= 4

    assert isinstance(result.confrozenset_field, frozenset)
    assert len(result.confrozenset_field) >= 5

    assert isinstance(result.conpositive_float_field, float)
    assert result.conpositive_float_field > 0


@pytest.mark.skipif(sys.version_info < (3, 12), reason="3.12 only syntax")
def test_type_alias(create_module: Callable[[str], ModuleType]) -> None:
    module = create_module(
        """
from typing import Literal
from dataclasses import dataclass


type LiteralAlias = Literal["a", "b"]


@dataclass
class A:
    field: LiteralAlias
""",
    )

    factory = DataclassFactory.create_factory(module.A)  # type: ignore[var-annotated]
    result = factory.build()
    assert result.field in {"a", "b"}
