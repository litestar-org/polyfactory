"""Parse ``Annotated`` metadata into polyfactory ``Constraints``.

This lives apart from ``polyfactory.field_meta`` so that annotation parsing (``polyfactory.utils._internal.type_node``) can use it
without importing ``FieldMeta``, which itself depends on the parser.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import asdict
from typing import TYPE_CHECKING, Any, cast

from polyfactory.utils.helpers import is_dataclass_instance, unwrap_annotated
from polyfactory.utils.predicates import is_annotated

if TYPE_CHECKING:
    from collections.abc import Sequence

    from polyfactory.field_meta import Constraints


def parse_constraints(metadata: Sequence[Any]) -> Constraints:
    """Parse constraints from ``Annotated`` metadata.

    Understands ``annotated_types`` and pydantic constraint objects, ``str`` method predicates (``str.islower`` etc.),
    URL constraint dataclasses, and mappings of constraint names to values.

    :param metadata: The metadata of an ``Annotated`` annotation.

    :returns: The constraints found in it.
    """
    constraints = {}

    for value in metadata:
        if is_annotated(value):
            _, inner_metadata = unwrap_annotated(value)
            constraints.update(cast("dict[str, Any]", parse_constraints(inner_metadata)))
        elif func := getattr(value, "func", None):
            if func is str.islower:
                constraints["lower_case"] = True
            elif func is str.isupper:
                constraints["upper_case"] = True
            elif func is str.isascii:
                constraints["pattern"] = "[[:ascii:]]"
            elif func is str.isdigit:
                constraints["pattern"] = "[[:digit:]]"
        elif is_dataclass_instance(value) and (value_dict := asdict(value)) and ("allowed_schemes" in value_dict):
            constraints["url"] = {k: v for k, v in value_dict.items() if v is not None}
        # This is to support `Constraints`, but we can't do a isinstance with `Constraints` since isinstance
        # checks with `TypedDict` is not supported.
        elif isinstance(value, Mapping):
            constraints.update(value)
        else:
            constraints.update(
                {
                    k: v
                    for k, v in {
                        "allow_inf_nan": getattr(value, "allow_inf_nan", None),
                        "decimal_places": getattr(value, "decimal_places", None),
                        "ge": getattr(value, "ge", None),
                        "gt": getattr(value, "gt", None),
                        "item_type": getattr(value, "item_type", None),
                        "le": getattr(value, "le", None),
                        "lower_case": getattr(value, "to_lower", None),
                        "lt": getattr(value, "lt", None),
                        "max_digits": getattr(value, "max_digits", None),
                        "max_length": getattr(value, "max_length", getattr(value, "max_length", None)),
                        "min_length": getattr(value, "min_length", getattr(value, "min_items", None)),
                        "multiple_of": getattr(value, "multiple_of", None),
                        "path_type": getattr(value, "path_type", None),
                        "pattern": getattr(value, "regex", getattr(value, "pattern", None)),
                        "tz": getattr(value, "tz", None),
                        "unique_items": getattr(value, "unique_items", None),
                        "upper_case": getattr(value, "to_upper", None),
                        "uuid_version": getattr(value, "uuid_version", None),
                    }.items()
                    if v is not None
                },
            )
    return cast("Constraints", constraints)
