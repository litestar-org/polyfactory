from __future__ import annotations
from collections import deque
from typing import TYPE_CHECKING, Any, MutableMapping, Tuple

from typing_extensions import is_typeddict

from polyfactory.constants import TYPE_MAPPING
from polyfactory.field_meta import FieldMeta
from polyfactory.utils.helpers import unwrap_annotation, unwrap_args
from polyfactory.utils.predicates import get_type_origin, is_any, is_union
from polyfactory.value_generators.primitives import create_random_string

if TYPE_CHECKING:
    from polyfactory.factories.base import BaseFactory


def handle_container_type(
    container_type: type,
    factory: type[BaseFactory],
    field_meta: FieldMeta,
) -> Any:
    """Handle generation of container types recursively.

    :param container_type: A type that can accept type arguments.
    :param factory: A factory.
    :param field_meta: A field meta instance.

    :returns: A built result.
    """
    if mapped_container_type := TYPE_MAPPING.get(container_type):
        container_type = mapped_container_type

    container = container_type() if container_type is not frozenset else set()

    if isinstance(container, MutableMapping) or is_typeddict(container):
        key_type, value_type = unwrap_args(field_meta.annotation) or (str, str)
        key = handle_complex_type(field_meta=FieldMeta.from_type(annotation=key_type), factory=factory)
        value = handle_complex_type(field_meta=FieldMeta.from_type(annotation=value_type), factory=factory)
        container[key] = value  # pyright: ignore
    elif field_meta.children:
        if isinstance(container, (list, deque)):
            container.append(
                handle_complex_type(
                    field_meta=factory.__random__.choice(field_meta.children),
                    factory=factory,
                )
            )
        else:
            container.add(
                handle_complex_type(
                    field_meta=factory.__random__.choice(field_meta.children),
                    factory=factory,
                )
            )

    return container if container_type is not frozenset else container_type(*container)


def handle_complex_type(
    factory: type[BaseFactory],
    field_meta: FieldMeta,
) -> Any:
    """Recursive type generation based on typing info stored in the graph like structure of pydantic field_metas.

    :param factory: A factory.
    :param field_meta: A field meta instance.

    :returns: A built result.
    """

    if origin := get_type_origin(annotation=unwrap_annotation(field_meta.annotation)):
        if origin not in (tuple, Tuple):
            return handle_container_type(field_meta=field_meta, container_type=origin, factory=factory)

        return tuple(
            handle_complex_type(field_meta=sub_field, factory=factory) for sub_field in (field_meta.children or [])
        )

    if is_union(field_meta.annotation) and field_meta.children:
        return handle_complex_type(field_meta=factory.__random__.choice(field_meta.children), factory=factory)

    if is_any(field_meta.annotation):
        return create_random_string(random=factory.__random__, min_length=1, max_length=10)

    if factory.should_set_none_value(field_meta):
        return None

    return factory.get_field_value(field_meta=field_meta, field_build_parameters=None)
