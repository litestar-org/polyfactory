import sys
from typing import Annotated, Any, get_args, get_origin

import annotated_types as at
import pytest

from polyfactory.utils.helpers import TypeCompatibilityAdapter


@pytest.mark.skipif(sys.version_info < (3, 12), reason="PEP 695 requires Python 3.12+")
class TestTypeCompatibilityAdapter:
    @staticmethod
    def assert_annotated_type(result: Any, expected_base: type, expected_metadata_type: type) -> None:
        """Assert that result is an Annotated type with expected base and metadata types."""
        assert get_origin(result) is Annotated
        args = get_args(result)
        assert args[0] == expected_base
        assert isinstance(args[1], expected_metadata_type)

    def test_simple_type_alias(self) -> None:
        """Test resolution of simple type alias."""
        type SimpleInt = int  # pyright: ignore[reportGeneralTypeIssues]

        result = TypeCompatibilityAdapter(SimpleInt).normalize()

        assert result is int

    def test_annotated_type_alias(self) -> None:
        """Test resolution of annotated type alias."""
        type PositiveInt = Annotated[int, at.Gt(0)]  # pyright: ignore[reportGeneralTypeIssues]
        result = TypeCompatibilityAdapter(PositiveInt).normalize()
        self.assert_annotated_type(result, int, at.Gt)

    def test_generic_type_alias(self) -> None:
        """Test resolution of generic type alias with type parameter."""
        type GenericList[T] = list[T]  # pyright: ignore[reportGeneralTypeIssues]

        result = TypeCompatibilityAdapter(GenericList[str]).normalize()

        assert result == list[str]

    def test_annotated_generic_type_alias(self) -> None:
        """Test resolution of annotated generic type alias."""
        type NonEmptyList[T] = Annotated[list[T], at.Len(1)]  # pyright: ignore[reportGeneralTypeIssues]
        result = TypeCompatibilityAdapter(NonEmptyList[int]).normalize()

        self.assert_annotated_type(result, list[int], at.Len)

    def test_nested_type_aliases(self) -> None:
        """Test resolution of nested type aliases."""
        type NegativeInt = Annotated[int, at.Lt(0)]  # pyright: ignore[reportGeneralTypeIssues]
        type NonEmptyList[T] = Annotated[list[T], at.Len(1)]  # pyright: ignore[reportGeneralTypeIssues]
        result = TypeCompatibilityAdapter(NonEmptyList[NegativeInt]).normalize()

        self.assert_annotated_type(result, list[Annotated[int, at.Lt(0)]], at.Len)

    def test_double_nested_type_aliases(self) -> None:
        """Test resolution of double nested type aliases."""
        type NonEmptyList[T] = Annotated[list[T], at.Len(1)]  # pyright: ignore[reportGeneralTypeIssues]

        result = TypeCompatibilityAdapter(NonEmptyList[NonEmptyList[int]]).normalize()

        assert get_origin(result) is Annotated
        outer_list, _ = get_args(result)

        assert get_origin(outer_list) is list
        inner_annotated = get_args(outer_list)[0]

        assert get_origin(inner_annotated) is Annotated
        inner_list, _ = get_args(inner_annotated)
        assert inner_list == list[int]

    @pytest.mark.parametrize(
        "type_hint,expected",
        [
            (int, int),
            (str, str),
            (list[int], list[int]),
            (dict[str, int], dict[str, int]),
            (tuple[int, ...], tuple[int, ...]),
            (set[str], set[str]),
        ],
        ids=["int", "str", "list", "dict", "tuple", "set"],
    )
    def test_builtin_types_unchanged(self, type_hint: type, expected: type) -> None:
        """Test that built-in types without alias are returned unchanged."""
        result = TypeCompatibilityAdapter(type_hint).normalize()

        assert result == expected
