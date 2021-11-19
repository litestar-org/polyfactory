from typing import Any


def inherits_from(parent: Any, value) -> bool:
    """Determines whether a given value is a descendent of a given parent"""
    return callable(value) and hasattr(value, "__bases__") and parent in value.__bases__
