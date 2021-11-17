from typing import Any, List

from pydantic import ConstrainedList


def handle_constrained_list(field: ConstrainedList) -> List[Any]:
    """Handle ConstrainedList instances"""
    return []
