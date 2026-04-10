from typing import Literal, Union

import pytest

from polyfactory.utils.predicates import is_literal


@pytest.mark.parametrize(
    "annotation,expected",
    [
        (Literal[1, 2, 3], True),
        (Union[int, str], False),
        (Union[Literal[1], Literal[2]], False),  # noqa: PYI030
        (int, False),
    ],
)
def test_is_literal(annotation: type, expected: bool) -> None:
    assert is_literal(annotation) is expected
