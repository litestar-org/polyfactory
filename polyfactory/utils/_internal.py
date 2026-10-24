from __future__ import annotations

from typing import TYPE_CHECKING

from typing_extensions import get_args

from polyfactory.utils.helpers import unwrap_annotation
from polyfactory.utils.predicates import get_type_origin, is_annotated, is_union
from polyfactory.utils.types import NoneType

if TYPE_CHECKING:
    from polyfactory.field_meta import FieldMeta


def is_attribute_overridden(base: type, cls: type, attribute_name: str) -> bool:
    """Return True if attribute is overridden by any ancestor before reaching base in the MRO."""
    for ancestor in cls.mro():
        if ancestor is base:
            return False
        if attribute_name in ancestor.__dict__:
            return True
    return False


def get_union_member_metas(field_meta: FieldMeta) -> list[FieldMeta | None] | None:
    """Return a union field's members as field metas, with ``None`` for ``None``, in the order written.

    ``FieldMeta.from_type`` builds a union's children from its type args other than ``None``, in order, and so do the
    pydantic integrations.

    :param field_meta: A field meta.

    :returns: The members, or ``None`` if the field is not a union or its children don't line up with its members.
    """
    annotation = field_meta.annotation
    if not is_union(get_args(annotation)[0] if is_annotated(annotation) else annotation):
        return None

    members: list[FieldMeta | None] = []
    children = iter(field_meta.children or [])
    for arg in field_meta.type_args:
        if arg is NoneType:
            members.append(None)
            continue
        child = next(children, None)
        if child is None:
            return None
        # A child for some other type - e.g. the item type of a collection member - was built some other way.
        arg_type, child_type = unwrap_annotation(arg), unwrap_annotation(child.annotation)
        if (get_type_origin(arg_type) or arg_type) != (get_type_origin(child_type) or child_type):
            return None
        members.append(child)
    return members if next(children, None) is None else None
