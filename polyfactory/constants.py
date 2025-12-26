from __future__ import annotations

from collections import abc, defaultdict, deque
from collections.abc import Iterable, Mapping, Sequence
from random import Random

# Mapping of type annotations into concrete types.
TYPE_MAPPING = {
    defaultdict: defaultdict,
    deque: deque,
    dict: dict,
    frozenset: frozenset,
    Iterable: list,
    list: list,
    Mapping: dict,
    Sequence: list,
    set: set,
    tuple: tuple,
    abc.Iterable: list,
    abc.Mapping: dict,
    abc.Sequence: list,
    abc.Set: set,
}


DEFAULT_RANDOM = Random()
RANDOMIZE_COLLECTION_LENGTH = False
MIN_COLLECTION_LENGTH = 0
MAX_COLLECTION_LENGTH = 5
