import sys
from collections import abc, defaultdict, deque
from typing import (
    DefaultDict,
    Deque,
    Dict,
    FrozenSet,
    Iterable,
    List,
    Mapping,
    Sequence,
    Set,
    Tuple,
    Union,
)

if sys.version_info >= (3, 10):  # pragma: no cover
    from types import UnionType
else:  # pragma: no cover
    UNION_TYPES = Union


# Mapping of type annotations into concrete types. This is used to normalize python <= 3.9 annotations.
TYPE_MAPPING = {
    DefaultDict: defaultdict,
    Deque: deque,
    Dict: dict,
    FrozenSet: frozenset,
    Iterable: list,
    List: list,
    Mapping: dict,
    Sequence: list,
    Set: set,
    Tuple: tuple,
    abc.Iterable: list,
    abc.Mapping: dict,
    abc.Sequence: list,
    abc.Set: set,
    UnionType: Union,
}

IGNORED_TYPE_ARGS: Set = {Ellipsis}
