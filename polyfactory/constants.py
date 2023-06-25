from __future__ import annotations

from collections import abc, defaultdict, deque
from random import Random
from typing import (
    Any,
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

try:
    from types import UnionType
except ImportError:
    UnionType = Union  # type: ignore


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

IGNORED_TYPE_ARGS: set[Any] = {Ellipsis}

DEFAULT_RANDOM = Random()
