import copy
import functools
from functools import lru_cache
from typing import Callable, TypeVar

from typing_extensions import ParamSpec

P = ParamSpec("P")
R = TypeVar("R")


def copying_lru_cache(fn: Callable[P, R]) -> Callable[P, R]:
    cached_func = lru_cache(fn)

    @functools.wraps(fn)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        return copy.copy(cached_func(*args, **kwargs))  # type: ignore[arg-type]

    return wrapper
