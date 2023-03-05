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
)

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
}
