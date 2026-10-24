"""Where ``Annotated`` constraints apply: through optionals, unions, aliases, NewTypes and collections.

Each case constrains an ``int`` to 100-105 and checks every generated ``int`` respects it, in ``build`` and in
``coverage``.
"""

from __future__ import annotations

from collections.abc import Iterable, Iterator
from dataclasses import make_dataclass
from typing import Annotated, Any, Callable, NewType, Optional, Union

import pytest
from annotated_types import Ge, Le
from typing_extensions import TypeAliasType

from pydantic import create_model

from polyfactory.exceptions import ParameterException
from polyfactory.factories import DataclassFactory
from polyfactory.factories.base import BaseFactory
from polyfactory.factories.pydantic_factory import ModelFactory
from tests.test_pydantic_factory import IS_PYDANTIC_V1

ConstrainedInt = Annotated[int, Ge(100), Le(105)]
ConstrainedAlias = TypeAliasType("ConstrainedAlias", ConstrainedInt)
ConstrainedNewType = NewType("ConstrainedNewType", ConstrainedInt)


def _collect_ints(values: Iterable[Any]) -> Iterator[int]:
    """Yield the ints among ``values``, including those in lists."""
    for value in values:
        if isinstance(value, list):
            yield from _collect_ints(value)
        elif isinstance(value, int):
            yield value


def _dataclass_factory(annotation: Any) -> type[BaseFactory[Any]]:
    return DataclassFactory.create_factory(make_dataclass("Model", [("value", annotation)]))


def _pydantic_factory(annotation: Any) -> type[BaseFactory[Any]]:
    return ModelFactory.create_factory(create_model("Model", value=(annotation, ...)))


@pytest.mark.parametrize(
    "create_factory",
    (
        pytest.param(_dataclass_factory, id="dataclass"),
        pytest.param(
            _pydantic_factory,
            id="pydantic",
            marks=pytest.mark.skipif(IS_PYDANTIC_V1, reason="pydantic v1 builds fields from ModelField"),
        ),
    ),
)
@pytest.mark.parametrize(
    "annotation",
    (
        pytest.param(ConstrainedInt, id="annotated"),
        pytest.param(Optional[ConstrainedInt], id="optional_annotated"),
        pytest.param(Annotated[Optional[int], Ge(100), Le(105)], id="annotated_optional"),
        pytest.param(Union[ConstrainedInt, str], id="union_with_annotated_member"),
        pytest.param(ConstrainedAlias, id="type_alias"),
        pytest.param(ConstrainedNewType, id="new_type"),
        pytest.param(list[ConstrainedInt], id="list_items"),
        pytest.param(Optional[list[ConstrainedInt]], id="optional_list_items"),
    ),
)
def test_constraint_placement(create_factory: Callable[[Any], type[BaseFactory[Any]]], annotation: Any) -> None:
    factory = create_factory(annotation)

    built = list(_collect_ints(factory.build().value for _ in range(100)))
    assert built
    assert all(100 <= value <= 105 for value in built)

    covered = list(_collect_ints(instance.value for instance in factory.coverage()))
    assert covered
    assert all(100 <= value <= 105 for value in covered)


@pytest.mark.xfail(raises=ParameterException, strict=True, reason="constraints on a union apply to each member")
def test_constraints_on_union_apply_to_each_member() -> None:
    factory = _dataclass_factory(Annotated[Union[int, str], Ge(100), Le(105)])

    assert all(100 <= value <= 105 for value in _collect_ints(factory.build().value for _ in range(100)))
