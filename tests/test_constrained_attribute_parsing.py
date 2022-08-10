import re
from decimal import Decimal
from typing import Dict, List, Tuple

from pydantic import (
    BaseModel,
    ConstrainedBytes,
    ConstrainedDecimal,
    ConstrainedFloat,
    ConstrainedInt,
    ConstrainedStr,
    Field,
    conbytes,
    condecimal,
    confloat,
    conint,
    conlist,
    conset,
    constr,
)

from pydantic_factories import ModelFactory
from tests.models import Person

pattern = r"(a|b|c)zz"


def test_constrained_attribute_parsing():
    class ConstrainedModel(BaseModel):
        conbytes_field: conbytes()
        condecimal_field: condecimal()
        confloat_field: confloat()
        conint_field: conint()
        conlist_field: conlist(str)
        conset_field: conset(str)
        constr_field: constr(to_lower=True)
        str_field1: str = Field(min_length=11)
        str_field2: str = Field(max_length=11)
        str_field3: str = Field(min_length=8, max_length=11, regex=pattern)
        int_field: int = Field(gt=1, multiple_of=5)
        float_field: float = Field(gt=100, lt=1000)
        decimal_field: Decimal = Field(ge=100, le=1000)
        list_field: List[str] = Field(min_items=1, max_items=10)
        constant_field: int = Field(const=True, default=100)

    class MyFactory(ModelFactory):
        __model__ = ConstrainedModel

    result = MyFactory.build()

    assert isinstance(result.conbytes_field, bytes)
    assert isinstance(result.conint_field, int)
    assert isinstance(result.confloat_field, float)
    assert isinstance(result.condecimal_field, Decimal)
    assert isinstance(result.conlist_field, list)
    assert isinstance(result.conset_field, set)
    assert isinstance(result.str_field1, str)
    assert isinstance(result.constr_field, str)
    assert result.constr_field.lower() == result.constr_field
    assert len(result.str_field1) >= 11
    assert len(result.str_field2) <= 11
    assert len(result.str_field3) >= 8
    assert len(result.str_field3) <= 11
    match = re.search(pattern, result.str_field3)
    assert match
    assert match.group(0)
    assert result.int_field >= 1
    assert result.int_field % 5 == 0
    assert result.float_field > 100
    assert result.float_field < 1000
    assert result.decimal_field > 100
    assert result.decimal_field < 1000
    assert len(result.list_field) >= 1
    assert len(result.list_field) <= 10
    assert all([isinstance(r, str) for r in result.list_field])
    assert result.constant_field == 100


def test_complex_constrained_attribute_parsing():
    class MyModel(BaseModel):
        conlist_with_model_field: conlist(Person, min_items=3)
        conlist_with_complex_type: conlist(Dict[str, Tuple[Person, Person, Person]], min_items=1)

    class MyFactory(ModelFactory):
        __model__ = MyModel

    result = MyFactory.build()

    assert len(result.conlist_with_model_field) >= 3
    assert all([isinstance(v, Person) for v in result.conlist_with_model_field])
    assert result.conlist_with_complex_type
    assert isinstance(result.conlist_with_complex_type[0], dict)
    assert isinstance(list(result.conlist_with_complex_type[0].values())[0], tuple)
    assert len(list(result.conlist_with_complex_type[0].values())[0]) == 3
    assert all([isinstance(v, Person) for v in list(result.conlist_with_complex_type[0].values())[0]])


def test_nested_constrained_attribute_handling():
    # subclassing the constrained fields is not documented by pydantic, but is supported apparently
    class MyConstrainedString(ConstrainedStr):
        regex = re.compile("^vpc-.*$")

    class MyConstrainedBytes(ConstrainedBytes):
        min_length = 11

    class MyConstrainedInt(ConstrainedInt):
        ge = 11

    class MyConstrainedFloat(ConstrainedFloat):
        ge = 11.0

    class MyConstrainedDecimal(ConstrainedDecimal):
        ge = Decimal("11.0")

    class MyModel(BaseModel):
        conbytes_list_field: List[conbytes()]
        condecimal_list_field: List[condecimal()]
        confloat_list_field: List[confloat()]
        conint_list_field: List[conint()]
        conlist_list_field: List[conlist(str)]
        conset_list_field: List[conset(str)]
        constr_list_field: List[constr(to_lower=True)]

        my_bytes_list_field: List[MyConstrainedBytes]
        my_decimal_list_field: List[MyConstrainedDecimal]
        my_float_list_field: List[MyConstrainedFloat]
        my_int_list_field: List[MyConstrainedInt]
        my_str_list_field: List[MyConstrainedString]

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
