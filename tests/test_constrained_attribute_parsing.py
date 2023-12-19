import re
import sys
from decimal import Decimal
from typing import Dict, List, Optional, Tuple

import pytest
from pydantic import (
    VERSION,
    BaseModel,
    Field,
    conbytes,
    condecimal,
    confloat,
    confrozenset,
    conint,
    conlist,
    conset,
    constr,
)

from polyfactory.factories.pydantic_factory import ModelFactory
from tests.models import Person

pattern = r"(a|b|c)zz"


@pytest.mark.skipif(VERSION.startswith("2"), reason="pydantic 1 only test")
def test_constrained_attribute_parsing_pydantic_v1() -> None:
    class ConstrainedModel(BaseModel):
        conbytes_field: conbytes()  # type: ignore[valid-type]
        condecimal_field: condecimal()  # type: ignore[valid-type]
        confloat_field: confloat()  # type: ignore[valid-type]
        conint_field: conint()  # type: ignore[valid-type]
        conlist_field: conlist(str, min_items=5, max_items=10)  # type: ignore[valid-type]
        conset_field: conset(str, min_items=5, max_items=10)  # type: ignore[valid-type]
        confrozenset_field: confrozenset(str, min_items=5, max_items=10)  # type: ignore[valid-type]
        constr_field: constr(to_lower=True)  # type: ignore[valid-type]
        str_field1: str = Field(min_length=11)
        str_field2: str = Field(max_length=11)
        str_field3: str = Field(min_length=8, max_length=11, regex=pattern)  # type: ignore[call-arg]
        int_field: int = Field(gt=1, multiple_of=5)
        float_field: float = Field(gt=100, lt=1000)
        decimal_field: Decimal = Field(ge=100, le=1000)
        list_field: List[str] = Field(min_items=1, max_items=10)  # type: ignore[call-arg]
        constant_field: int = Field(const=True, default=100)  # type: ignore[call-arg]
        optional_field: Optional[constr(min_length=1)]  # type: ignore[valid-type]

    class MyFactory(ModelFactory):
        __model__ = ConstrainedModel

    result = MyFactory.build()

    assert isinstance(result.conbytes_field, bytes)
    assert isinstance(result.conint_field, int)
    assert isinstance(result.confloat_field, float)
    assert isinstance(result.condecimal_field, Decimal)
    assert isinstance(result.conlist_field, list)
    assert isinstance(result.conset_field, set)
    assert isinstance(result.confrozenset_field, frozenset)
    assert isinstance(result.str_field1, str)
    assert isinstance(result.constr_field, str)
    assert len(result.conlist_field) >= 5
    assert len(result.conlist_field) <= 10
    assert len(result.conset_field) >= 5
    assert len(result.conset_field) <= 10
    assert len(result.confrozenset_field) >= 5
    assert len(result.confrozenset_field) <= 10
    assert result.constr_field.lower() == result.constr_field
    assert len(result.str_field1) >= 11
    assert len(result.str_field2) <= 11
    assert len(result.str_field3) >= 8
    assert len(result.str_field3) <= 11
    match = re.search(pattern, result.str_field3)
    assert match
    assert match[0]
    assert result.int_field >= 1
    assert result.int_field % 5 == 0
    assert result.float_field > 100
    assert result.float_field < 1000
    assert result.decimal_field > 100
    assert result.decimal_field < 1000
    assert len(result.list_field) >= 1
    assert len(result.list_field) <= 10
    assert all(isinstance(r, str) for r in result.list_field)
    assert result.constant_field == 100
    assert result.optional_field is None or len(result.optional_field) >= 1


@pytest.mark.skipif(VERSION.startswith("2"), reason="pydantic 1 only test")
def test_complex_constrained_attribute_parsing_pydantic_v1() -> None:
    class MyModel(BaseModel):
        conlist_with_model_field: conlist(Person, min_items=3)  # type: ignore[valid-type]
        conlist_with_complex_type: conlist(  # type: ignore[valid-type]
            Dict[str, Tuple[Person, Person, Person]],
            min_items=1,
        )

    class MyFactory(ModelFactory):
        __model__ = MyModel

    result = MyFactory.build()

    assert len(result.conlist_with_model_field) >= 3
    assert all(isinstance(v, Person) for v in result.conlist_with_model_field)
    assert result.conlist_with_complex_type
    assert isinstance(result.conlist_with_complex_type[0], dict)
    assert isinstance(next(iter(result.conlist_with_complex_type[0].values())), tuple)
    assert len(next(iter(result.conlist_with_complex_type[0].values()))) == 3
    assert all(isinstance(v, Person) for v in next(iter(result.conlist_with_complex_type[0].values())))


@pytest.mark.skipif(VERSION.startswith("2"), reason="pydantic 1 only test")
def test_nested_constrained_attribute_handling_pydantic_1() -> None:
    # subclassing the constrained fields is not documented by pydantic, but is supported apparently

    from pydantic import (
        ConstrainedBytes,
        ConstrainedDecimal,
        ConstrainedFloat,
        ConstrainedInt,
        ConstrainedStr,
    )

    class MyConstrainedString(ConstrainedStr):  # type: ignore[misc,valid-type]
        regex = re.compile("^vpc-.*$")

    class MyConstrainedBytes(ConstrainedBytes):  # type: ignore[misc,valid-type]
        min_length = 11

    class MyConstrainedInt(ConstrainedInt):  # type: ignore[misc,valid-type]
        ge = 11

    class MyConstrainedFloat(ConstrainedFloat):  # type: ignore[misc,valid-type]
        ge = 11.0

    class MyConstrainedDecimal(ConstrainedDecimal):  # type: ignore[misc,valid-type]
        ge = Decimal("11.0")

    class MyModel(BaseModel):
        conbytes_list_field: List[conbytes()]  # type: ignore[valid-type]
        condecimal_list_field: List[condecimal()]  # type: ignore[valid-type]
        confloat_list_field: List[confloat()]  # type: ignore[valid-type]
        conint_list_field: List[conint()]  # type: ignore[valid-type]
        conlist_list_field: List[conlist(str)]  # type: ignore[valid-type]
        conset_list_field: List[conset(str)]  # type: ignore[valid-type]
        constr_list_field: List[constr(to_lower=True)]  # type: ignore[valid-type]

        my_bytes_list_field: List[MyConstrainedBytes]
        my_decimal_list_field: List[MyConstrainedDecimal]
        my_float_list_field: List[MyConstrainedFloat]
        my_int_list_field: List[MyConstrainedInt]
        my_str_list_field: List[MyConstrainedString]

        my_bytes_dict_field: Dict[str, MyConstrainedBytes]
        my_decimal_dict_field: Dict[str, MyConstrainedDecimal]
        my_float_dict_field: Dict[str, MyConstrainedFloat]
        my_int_dict_field: Dict[str, MyConstrainedInt]
        my_str_dict_field: Dict[str, MyConstrainedString]

    class MyFactory(ModelFactory):
        __model__ = MyModel

    result = MyFactory.build()

    assert result.conbytes_list_field
    assert result.condecimal_list_field
    assert result.confloat_list_field
    assert result.conint_list_field
    assert result.conlist_list_field
    assert result.conset_list_field
    assert result.constr_list_field
    assert result.my_bytes_list_field
    assert result.my_decimal_list_field
    assert result.my_float_list_field
    assert result.my_int_list_field
    assert result.my_str_list_field
    assert result.my_bytes_dict_field
    assert result.my_decimal_dict_field
    assert result.my_float_dict_field
    assert result.my_int_dict_field
    assert result.my_str_dict_field


@pytest.mark.skipif(
    VERSION.startswith("1") or sys.version_info < (3, 9),
    reason="pydantic 2 only test, does not work correctly in py 3.8",
)
def test_nested_constrained_attribute_handling_pydantic_2() -> None:
    # subclassing the constrained fields is not documented by pydantic, but is supported apparently

    class MyModel(BaseModel):
        conbytes_list_field: List[conbytes()]  # type: ignore[valid-type]
        condecimal_list_field: List[condecimal()]  # type: ignore[valid-type]
        confloat_list_field: List[confloat()]  # type: ignore[valid-type]
        conint_list_field: List[conint()]  # type: ignore[valid-type]
        conlist_list_field: List[conlist(str)]  # type: ignore[valid-type]
        conset_list_field: List[conset(str)]  # type: ignore[valid-type]
        constr_list_field: List[constr(to_lower=True)]  # type: ignore[valid-type]

    class MyFactory(ModelFactory):
        __model__ = MyModel

    result = MyFactory.build()

    assert result.conbytes_list_field
    assert result.condecimal_list_field
    assert result.confloat_list_field
    assert result.conint_list_field
    assert result.conlist_list_field
    assert result.conset_list_field
    assert result.constr_list_field


@pytest.mark.skipif(
    VERSION.startswith("1") or sys.version_info < (3, 9),
    reason="pydantic 2 only test, does not work correctly in py 3.8",
)
def test_constrained_attribute_parsing_pydantic_v2() -> None:
    class ConstrainedModel(BaseModel):
        conbytes_field: conbytes()  # type: ignore[valid-type]
        condecimal_field: condecimal()  # type: ignore[valid-type]
        confloat_field: confloat()  # type: ignore[valid-type]
        conint_field: conint()  # type: ignore[valid-type]
        conlist_field: conlist(str, min_length=5, max_length=10)  # type: ignore[valid-type]
        conset_field: conset(str, min_length=5, max_length=10)  # type: ignore[valid-type]
        confrozenset_field: confrozenset(str, min_length=5, max_length=10)  # type: ignore[valid-type]
        constr_field: constr(to_lower=True)  # type: ignore[valid-type]
        str_field1: str = Field(min_length=11)
        str_field2: str = Field(max_length=11)
        str_field3: str = Field(min_length=8, max_length=11, pattern=pattern)
        int_field: int = Field(gt=1, multiple_of=5)
        float_field: float = Field(gt=100, lt=1000)
        decimal_field: Decimal = Field(ge=100, le=1000)
        list_field: List[str] = Field(min_length=1, max_length=10)
        optional_field: Optional[constr(min_length=1)]  # type: ignore[valid-type]

    class MyFactory(ModelFactory):
        __model__ = ConstrainedModel

    result = MyFactory.build()

    assert isinstance(result.conbytes_field, bytes)
    assert isinstance(result.conint_field, int)
    assert isinstance(result.confloat_field, float)
    assert isinstance(result.condecimal_field, Decimal)
    assert isinstance(result.conlist_field, list)
    assert isinstance(result.conset_field, set)
    assert isinstance(result.confrozenset_field, frozenset)
    assert isinstance(result.str_field1, str)
    assert isinstance(result.constr_field, str)
    assert len(result.conlist_field) >= 5
    assert len(result.conlist_field) <= 10
    assert len(result.conset_field) >= 5
    assert len(result.conset_field) <= 10
    assert len(result.confrozenset_field) >= 5
    assert len(result.confrozenset_field) <= 10
    assert result.constr_field.lower() == result.constr_field
    assert len(result.str_field1) >= 11
    assert len(result.str_field2) <= 11
    assert len(result.str_field3) >= 8
    assert len(result.str_field3) <= 11
    match = re.search(pattern, result.str_field3)
    assert match
    assert match[0]
    assert result.int_field >= 1
    assert result.int_field % 5 == 0
    assert result.float_field > 100
    assert result.float_field < 1000
    assert result.decimal_field > 100
    assert result.decimal_field < 1000
    assert len(result.list_field) >= 1
    assert len(result.list_field) <= 10
    assert all(isinstance(r, str) for r in result.list_field)
    assert result.optional_field is None or len(result.optional_field) >= 1


@pytest.mark.skipif(VERSION.startswith("1"), reason="pydantic 2 only test")
def test_complex_constrained_attribute_parsing_pydantic_v2() -> None:
    class MyModel(BaseModel):
        conlist_with_model_field: conlist(Person, min_length=3)  # type: ignore[valid-type]
        conlist_with_complex_type: conlist(  # type: ignore[valid-type]
            Dict[str, Tuple[Person, Person, Person]],
            min_length=1,
        )

    class MyFactory(ModelFactory):
        __model__ = MyModel

    result = MyFactory.build()

    assert len(result.conlist_with_model_field) >= 3
    assert all(isinstance(v, Person) for v in result.conlist_with_model_field)
    assert result.conlist_with_complex_type
    assert isinstance(result.conlist_with_complex_type[0], dict)
    assert isinstance(next(iter(result.conlist_with_complex_type[0].values())), tuple)
    assert len(next(iter(result.conlist_with_complex_type[0].values()))) == 3
    assert all(isinstance(v, Person) for v in next(iter(result.conlist_with_complex_type[0].values())))
