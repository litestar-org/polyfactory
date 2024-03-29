from typing import TYPE_CHECKING, Dict, FrozenSet, List, Set, Tuple

import pytest

from polyfactory.collection_extender import CollectionExtender

if TYPE_CHECKING:
    from typing import Any

pytestmark = pytest.mark.parametrize("number_of_args", [0, 1, 3])


def test_tuple_extender(number_of_args: int) -> None:
    annotation_alias: Any = Tuple[int, ...]
    type_args = (int, ...)

    extended_type_args = CollectionExtender.extend_type_args(annotation_alias, type_args, number_of_args)

    assert extended_type_args == (int,) * number_of_args


def test_tuple_extender__constant_length(number_of_args: int) -> None:
    annotation_alias: Any = Tuple[int, int, int]
    type_args = (int, int, int, int)

    extended_type_args = CollectionExtender.extend_type_args(annotation_alias, type_args, number_of_args)

    assert extended_type_args == (int, int, int, int)


def test_tuple_extender__not_typed(number_of_args: int) -> None:
    annotation_alias: Any = Tuple
    type_args = ()

    extended_type_args = CollectionExtender.extend_type_args(annotation_alias, type_args, number_of_args)

    assert extended_type_args == ()


def test_list_extender(number_of_args: int) -> None:
    annotation_alias: Any = List[int]
    type_args = (int,)

    extended_type_args = CollectionExtender.extend_type_args(annotation_alias, type_args, number_of_args)

    assert extended_type_args == (int,) * number_of_args


def test_set_extender(number_of_args: int) -> None:
    class Dummy: ...

    annotation_alias: Any = Set[Dummy]
    type_args = (Dummy,)

    extended_type_args = CollectionExtender.extend_type_args(annotation_alias, type_args, number_of_args)

    assert extended_type_args == (Dummy,) * number_of_args


def test_frozen_set_extender(number_of_args: int) -> None:
    class Dummy: ...

    annotation_alias: Any = FrozenSet[Dummy]
    type_args = (Dummy,)

    extended_type_args = CollectionExtender.extend_type_args(annotation_alias, type_args, number_of_args)

    assert extended_type_args == (Dummy,) * number_of_args


def test_dict_extender(number_of_args: int) -> None:
    annotation_alias: Any = Dict[str, int]
    type_args = (str, int)

    extended_type_args = CollectionExtender.extend_type_args(annotation_alias, type_args, number_of_args)

    assert extended_type_args == (str, int) * number_of_args
