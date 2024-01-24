import dataclasses
from dataclasses import dataclass as vanilla_dataclass
from dataclasses import field
from types import ModuleType
from typing import Callable, Dict, List, Optional, Tuple, Union
from unittest.mock import ANY

import pytest

from pydantic.dataclasses import dataclass as pydantic_dataclass

from polyfactory.factories import DataclassFactory
from tests.models import Person


def test_factory_vanilla_dc() -> None:
    @vanilla_dataclass
    class VanillaDC:
        id: int
        name: str
        list_field: List[Dict[str, int]]
        field_of_some_value: Optional[int] = field(default_factory=lambda: 0)

    class MyFactory(DataclassFactory[VanillaDC]):
        __model__ = VanillaDC

    result = MyFactory.build()

    assert result
    assert result.id
    assert result.name
    assert result.list_field
    assert result.list_field[0]
    assert [isinstance(value, int) for value in result.list_field[0].values()]


def test_factory_pydantic_dc() -> None:
    @pydantic_dataclass
    class PydanticDC:
        id: int
        name: str
        list_field: List[Dict[str, int]]
        field_of_some_value: Optional[int] = field(default_factory=lambda: 0)

    class MyFactory(DataclassFactory[PydanticDC]):
        __model__ = PydanticDC

    result = MyFactory.build()

    assert result
    assert result.id
    assert result.name
    assert result.list_field
    assert result.list_field[0]
    assert [isinstance(value, int) for value in result.list_field[0].values()]


def test_vanilla_dc_with_embedded_model() -> None:
    @vanilla_dataclass
    class VanillaDC:
        people: List[Person]

    class MyFactory(DataclassFactory[VanillaDC]):
        __model__ = VanillaDC

    result = MyFactory.build()

    assert result.people
    assert [isinstance(person, Person) for person in result.people]


def test_pydantic_dc_with_embedded_model() -> None:
    @vanilla_dataclass
    class PydanticDC:
        people: List[Person]

    class MyFactory(DataclassFactory):
        __model__ = PydanticDC

    result = MyFactory.build()

    assert result.people
    assert [isinstance(person, Person) for person in result.people]


def test_model_with_embedded_dataclasses() -> None:
    @vanilla_dataclass
    class VanillaDC:
        people: List[Person]

    @vanilla_dataclass
    class PydanticDC:
        people: List[Person]

    @vanilla_dataclass
    class Crowd:
        west: VanillaDC
        east: PydanticDC

    class MyFactory(DataclassFactory):
        __model__ = Crowd

    result = MyFactory.build()

    assert result.west
    assert result.west.people
    assert result.east
    assert result.east.people


def function_with_kwargs(first: int, second: float, third: str = "moishe") -> None:
    pass


def test_complex_embedded_dataclass() -> None:
    @vanilla_dataclass
    class VanillaDC:
        people: List[Person]

    @vanilla_dataclass
    class MyModel:
        weirdly_nest_field: List[Dict[str, Dict[str, VanillaDC]]]

    class MyFactory(DataclassFactory):
        __model__ = MyModel

    result = MyFactory.build()

    assert result.weirdly_nest_field
    assert result.weirdly_nest_field[0]
    assert next(iter(result.weirdly_nest_field[0].values())).values()
    assert next(iter(next(iter(result.weirdly_nest_field[0].values())).values()))
    assert isinstance(next(iter(next(iter(result.weirdly_nest_field[0].values())).values())), VanillaDC)


def test_tuple_ellipsis_in_vanilla_dc() -> None:
    @vanilla_dataclass
    class VanillaDC:
        ids: Tuple[int, ...]

    class MyFactory(DataclassFactory[VanillaDC]):
        __model__ = VanillaDC

    result = MyFactory.build()

    assert result
    assert result.ids


def test_dataclass_factory_with_future_annotations(create_module: Callable[[str], ModuleType]) -> None:
    module = create_module(
        """
from __future__ import annotations

from dataclasses import dataclass

@dataclass
class example:
    foo: str
""",
    )
    example: type = module.example
    assert example.__annotations__ == {"foo": "str"}

    class MyFactory(DataclassFactory[example]):  # type:ignore[valid-type]
        __model__ = example

    assert MyFactory.process_kwargs() == {"foo": ANY}


def test_dataclass_with_forward_reference(create_module: Callable[[str], ModuleType]) -> None:
    module = create_module(
        """
from __future__ import annotations

from dataclasses import dataclass
from polyfactory.factories import DataclassFactory


@dataclass
class Foo:
    bar: Bar


@dataclass
class Bar:
    ...
""",
    )

    Foo: type = module.Foo

    class FooFactory(DataclassFactory[Foo]):  # type:ignore[valid-type]
        __model__ = Foo

    foo = FooFactory.build()
    assert isinstance(foo, Foo)


def test_dataclass_with_init_false() -> None:
    @vanilla_dataclass
    class VanillaDC:
        id_: int = field(init=False)

    class MyFactory(DataclassFactory[VanillaDC]):
        __model__ = VanillaDC

    result = MyFactory.build()

    assert result


def test_use_default_with_callable_default() -> None:
    @vanilla_dataclass
    class Foo:
        default_field: int = dataclasses.field(default_factory=lambda: 10)

    class FooFactory(DataclassFactory[Foo]):
        __model__ = Foo
        __use_defaults__ = True

    foo = FooFactory.build()

    assert foo.default_field == 10


def test_use_default_with_non_callable_default() -> None:
    @vanilla_dataclass
    class Foo:
        default_field: int = 10

    class FooFactory(DataclassFactory[Foo]):
        __model__ = Foo
        __use_defaults__ = True

    foo = FooFactory.build()

    assert foo.default_field == 10


def test_union_types() -> None:
    @vanilla_dataclass
    class A:
        a: Union[List[str], List[int]]
        b: Union[str, List[int]]
        c: List[Union[Tuple[int, int], Tuple[str, int]]]

    AFactory = DataclassFactory.create_factory(A)

    assert AFactory.build()


def test_collection_unions_with_models() -> None:
    @vanilla_dataclass
    class A:
        a: int

    @vanilla_dataclass
    class B:
        a: str

    @vanilla_dataclass
    class C:
        a: Union[List[A], List[B]]
        b: List[Union[A, B]]

    CFactory = DataclassFactory.create_factory(C)

    c = CFactory.build()

    assert isinstance(c.a, list)
    assert all(isinstance(value, A) for value in c.a) or all(isinstance(value, B) for value in c.a)

    assert isinstance(c.b, list)
    assert all(isinstance(value, (A, B)) for value in c.b)


@pytest.mark.parametrize("allow_none", (True, False))
def test_optional_type(allow_none: bool) -> None:
    @vanilla_dataclass
    class A:
        a: Union[str, None]
        b: Optional[str]
        c: Optional[Union[str, int, List[int]]]

    class AFactory(DataclassFactory[A]):
        __model__ = A

        __allow_none_optionals__ = allow_none

    a = AFactory.build()

    if not allow_none:
        assert isinstance(a.a, str)
        assert isinstance(a.b, str)
        assert isinstance(a.c, (str, int, list))

        if isinstance(a.c, list):
            assert all(isinstance(value, int) for value in a.c)
