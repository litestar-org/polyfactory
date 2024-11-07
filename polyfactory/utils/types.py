from typing import Any, Union

try:
    from types import NoneType, UnionType

    UNION_TYPES = {UnionType, Union}
except ImportError:
    UNION_TYPES = {Union}

    NoneType = type(None)  # type: ignore[misc]


class Frozendict(dict):
    def __setitem__(self, _: Any, __: Any) -> None:
        msg = "Unable to set value"
        raise TypeError(msg)

    def __hash__(self) -> int:  # type: ignore[override]
        return hash(tuple(self.items()))


__all__ = ("NoneType", "UNION_TYPES", "Frozendict")
