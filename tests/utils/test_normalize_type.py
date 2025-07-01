import sys
import textwrap
from types import ModuleType
from typing import Any, Callable, Dict, List, Set, Tuple, get_args, get_origin

import annotated_types as at
import pytest
from typing_extensions import Annotated

from polyfactory.utils.normalize_type import normalize_type


@pytest.mark.skipif(sys.version_info < (3, 12), reason="PEP 695 requires Python 3.12+")
class TestNormalizeTypePep695:
    @staticmethod
    def assert_annotated_type(result: Any, expected_base: type, expected_metadata_type: type) -> None:
        """Assert that result is an Annotated type with expected base and metadata types."""
        assert get_origin(result) is Annotated
        args = get_args(result)
        assert args[0] == expected_base
        assert isinstance(args[1], expected_metadata_type)

    def test_simple_type_alias(self, create_module: Callable[[str], ModuleType]) -> None:
        """Test resolution of simple type alias."""

        module = create_module(
            textwrap.dedent(
                """
                type SimpleInt = int
                """
            )
        )
        result = normalize_type(module.SimpleInt)

        assert result is int

    def test_annotated_type_alias(self, create_module: Callable[[str], ModuleType]) -> None:
        """Test resolution of annotated type alias."""
        module = create_module(
            textwrap.dedent(
                """
                from typing import Annotated
                from annotated_types import Gt

                type PositiveInt = Annotated[int, Gt(0)]
                """
            )
        )
        result = normalize_type(module.PositiveInt)
        self.assert_annotated_type(result, int, at.Gt)

    def test_generic_type_alias(self, create_module: Callable[[str], ModuleType]) -> None:
        """Test resolution of generic type alias with type parameter."""
        module = create_module(
            textwrap.dedent(
                """
                type GenericList[T] = list[T]
                """
            )
        )

        result = normalize_type(module.GenericList[str])

        assert result == list[str]

    def test_annotated_generic_type_alias(self, create_module: Callable[[str], ModuleType]) -> None:
        """Test resolution of annotated generic type alias."""
        module = create_module(
            textwrap.dedent(
                """
                from typing import Annotated
                from annotated_types import Len

                type NonEmptyList[T] = Annotated[list[T], Len(1)]
                """
            )
        )
        result = normalize_type(module.NonEmptyList[int])

        self.assert_annotated_type(result, list[int], at.Len)

    def test_nested_type_aliases(self, create_module: Callable[[str], ModuleType]) -> None:
        """Test resolution of nested type aliases."""
        module = create_module(
            textwrap.dedent(
                """
                from typing import Annotated
                from annotated_types import Lt, Len

                type NegativeInt = Annotated[int, Lt(0)]
                type NonEmptyList[T] = Annotated[list[T], Len(1)]
                """
            )
        )
        result = normalize_type(module.NonEmptyList[module.NegativeInt])

        self.assert_annotated_type(result, list[Annotated[int, at.Lt(0)]], at.Len)

    def test_double_nested_type_aliases(self, create_module: Callable[[str], ModuleType]) -> None:
        """Test resolution of double nested type aliases."""
        module = create_module(
            textwrap.dedent(
                """
                from typing import Annotated
                from annotated_types import Len

                type NonEmptyList[T] = Annotated[list[T], Len(1)]
                """
            )
        )

        result = normalize_type(module.NonEmptyList[module.NonEmptyList[int]])

        assert get_origin(result) is Annotated
        outer_list, _ = get_args(result)

        assert get_origin(outer_list) is list
        inner_annotated = get_args(outer_list)[0]

        assert get_origin(inner_annotated) is Annotated
        inner_list, _ = get_args(inner_annotated)
        assert inner_list == list[int]

    def test_nested_generic_type_aliases(self, create_module: Callable[[str], ModuleType]) -> None:
        """Test nested generic type aliases."""
        module = create_module(
            textwrap.dedent(
                """
                type Inner[T] = list[T]
                type Outer[T] = Inner[Inner[T]]
                """
            )
        )

        result = normalize_type(module.Outer[int])
        assert result == list[list[int]]


@pytest.mark.parametrize(
    "type_hint,expected",
    [
        (int, int),
        (str, str),
        (List[int], List[int]),
        (Dict[str, int], Dict[str, int]),
        (Tuple[int, ...], Tuple[int, ...]),
        (Set[str], Set[str]),
    ],
    ids=["int", "str", "list", "dict", "tuple", "set"],
)
def test_builtin_types_unchanged(type_hint: type, expected: type) -> None:
    """Test that built-in types without alias are returned unchanged."""
    result = normalize_type(type_hint)

    assert result == expected
