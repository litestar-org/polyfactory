from typing import Tuple, TYPE_CHECKING

import pytest

from polyfactory.collection_extender import CollectionExtender

if TYPE_CHECKING:
    from typing import GenericAlias  # type: ignore

pytestmark = pytest.mark.parametrize("number_of_args", [0, 1, 3])


def test_tuple_extender(number_of_args: int) -> None:
    annotation_alias: GenericAlias = Tuple[int, ...]  # type: ignore
    type_args = (int, ...)

    extended_type_args = CollectionExtender.extend_type_args(annotation_alias, type_args, number_of_args)

    assert extended_type_args == (int,) * number_of_args


def test_tuple_extender__constant_length(number_of_args: int) -> None:
    annotation_alias: GenericAlias = Tuple[int, int, int]  # type: ignore
    type_args = (int, int, int, int)

    extended_type_args = CollectionExtender.extend_type_args(annotation_alias, type_args, number_of_args)

    assert extended_type_args == (int, int, int, int)


def test_tuple_extender__not_typed(number_of_args: int) -> None:
    annotation_alias: GenericAlias = Tuple  # type: ignore
    type_args = ()

    extended_type_args = CollectionExtender.extend_type_args(annotation_alias, type_args, number_of_args)

    assert extended_type_args == ()


def test_list_extender(number_of_args: int) -> None:
    annotation_alias: GenericAlias = list[int]  # type: ignore
    type_args = (int,)

    extended_type_args = CollectionExtender.extend_type_args(annotation_alias, type_args, number_of_args)

    assert extended_type_args == (int,) * number_of_args


def test_set_extender(number_of_args: int) -> None:
    class Dummy:
        ...

    annotation_alias: GenericAlias = set[Dummy]  # type: ignore
    type_args = (Dummy,)

    extended_type_args = CollectionExtender.extend_type_args(annotation_alias, type_args, number_of_args)

    assert extended_type_args == (Dummy,) * number_of_args


def test_dict_extender(number_of_args: int) -> None:
    annotation_alias: GenericAlias = dict[str, int]  # type: ignore
    type_args = (str, int)

    extended_type_args = CollectionExtender.extend_type_args(annotation_alias, type_args, number_of_args)

    assert extended_type_args == (str, int)
