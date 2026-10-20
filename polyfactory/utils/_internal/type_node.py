"""Parse annotations once into a small, closed set of immutable type nodes.

This follows how type checkers represent types (mypy's ``ProperType`` hierarchy, ty's ``Type`` enum) rather than
re-inspecting raw ``typing`` objects at every use site:

* ``Annotated`` is metadata, not a type: it becomes ``node.constraints`` on the inner type.
* Unions are flattened and simplified as they are built (``make_union``), like mypy's ``make_simplified_union``.
  ``Optional[X]`` stays a union with a ``None`` member; whether a node admits ``None`` is derived from that structure
  (``is_optional``, ``allows_none``, ``strip_optional()``, as in Litestar's ``FieldDefinition`` and type-lens's
  ``TypeView``) rather than stored, so it cannot drift from it.
* Abstract collection types are mapped to the concrete type to build (``Sequence[int]`` -> ``list``).
* Aliases and NewTypes are *nominal* nodes. They keep the original object, so providers registered for them can
  match, and point at what they expand to. Alias targets are resolved lazily, so recursive aliases need no cycle
  detection here.
* Qualifiers that only matter to a type checker (``Required``, ``NotRequired``, ``ReadOnly``, ``ClassVar``, ``Final``)
  are stripped in one place.

Nodes are immutable, so a parsed tree is cached and shared between fields and factories. The cache key includes each
annotation's arguments in written order: typing compares unions regardless of member order
(``Union[None, int] == Union[int, None]``), so keying on the annotation alone would hand back the other spelling.
"""

from __future__ import annotations

import functools
from collections import abc, deque
from dataclasses import dataclass, replace
from types import GenericAlias
from typing import TYPE_CHECKING, Annotated, Any, ClassVar, Final, ForwardRef, Literal, TypeVar, Union, cast

import typing_extensions
from typing_extensions import NotRequired, Required, get_args, get_origin, is_typeddict

from polyfactory.constants import TYPE_MAPPING
from polyfactory.utils._internal.constraints import parse_constraints
from polyfactory.utils.predicates import is_new_type, is_type_alias
from polyfactory.utils.types import UNION_TYPES, Frozendict, NoneType

if TYPE_CHECKING:
    from polyfactory.field_meta import Constraints

# ``ReadOnly`` needs typing-extensions>=4.9; the declared minimum is lower.
_QUALIFIERS = {
    qualifier
    for qualifier in (Required, NotRequired, getattr(typing_extensions, "ReadOnly", None), ClassVar, Final)
    if qualifier is not None
}


@dataclass(frozen=True, eq=False)
class TypeNode:
    """Base node.

    ``raw`` is the annotation this node was parsed from. Providers are looked up by it, so a provider registered for
    e.g. ``Annotated[str, ...]`` or a type alias keeps matching after parsing.
    """

    raw: Any
    constraints: Constraints | None

    @functools.cached_property
    def is_union(self) -> bool:
        """Whether this is a union."""
        return False

    @functools.cached_property
    def is_optional(self) -> bool:
        """Whether this is a union with a ``None`` member."""
        return False

    @functools.cached_property
    def allows_none(self) -> bool:
        """Whether ``None`` is a valid value: an optional union, ``None`` itself, or an alias or NewType of either."""
        return self.is_optional

    def strip_optional(self) -> TypeNode:
        """Return this node without its ``None`` member: ``Optional[X]`` -> ``X``. Other nodes are returned as is."""
        return self


@dataclass(frozen=True, eq=False)
class AnyNode(TypeNode):
    """``typing.Any``, and the item type of a bare ``list``/``dict``/... annotation."""


@dataclass(frozen=True, eq=False)
class NoneNode(TypeNode):
    """``None``, on its own or as a union member."""

    @functools.cached_property
    def allows_none(self) -> bool:
        return True


@dataclass(frozen=True, eq=False)
class InstanceNode(TypeNode):
    """A plain class: ``int``, ``str``, ``Decimal``, an enum, a model, ``Callable`` and other opaque types."""

    cls: Any


@dataclass(frozen=True, eq=False)
class CollectionNode(TypeNode):
    """A homogeneous collection: ``list``, ``set``, ``frozenset``, ``deque`` or a subclass of one."""

    cls: type
    item: TypeNode


@dataclass(frozen=True, eq=False)
class MappingNode(TypeNode):
    cls: type
    key: TypeNode
    value: TypeNode


@dataclass(frozen=True, eq=False)
class TupleNode(TypeNode):
    """``tuple[int, str]`` has ``items=(int, str)``; ``tuple[int, ...]`` has ``items=(int,)`` and ``variadic=True``."""

    cls: type
    items: tuple[TypeNode, ...]
    variadic: bool


@dataclass(frozen=True, eq=False)
class UnionNode(TypeNode):
    """At least two members, none of them unions. ``Optional[X]`` is a union of ``X`` and a ``NoneNode``."""

    members: tuple[TypeNode, ...]

    @functools.cached_property
    def is_union(self) -> bool:
        return True

    @functools.cached_property
    def is_optional(self) -> bool:
        return any(isinstance(member, NoneNode) for member in self.members)

    @functools.cached_property
    def allows_none(self) -> bool:
        return self.is_optional

    def strip_optional(self) -> TypeNode:
        if not self.is_optional:
            return self
        members = [member for member in self.members if not isinstance(member, NoneNode)]
        if len(members) == 1:
            return members[0]
        try:
            raw: Any = Union[tuple(member.raw for member in members)]
        except TypeError:  # an unhashable member annotation
            raw = self.raw
        return replace(self, raw=raw, members=tuple(members))


@dataclass(frozen=True, eq=False)
class LiteralNode(TypeNode):
    values: tuple[Any, ...]


@dataclass(frozen=True, eq=False)
class NewTypeNode(TypeNode):
    supertype: TypeNode

    @functools.cached_property
    def allows_none(self) -> bool:
        return self.supertype.allows_none


@dataclass(frozen=True, eq=False)
class AliasNode(TypeNode):
    """A PEP 695 type alias, possibly specialised (``Pair[int]``). ``target`` is resolved when first accessed."""

    alias: Any
    args: tuple[Any, ...]

    @functools.cached_property
    def allows_none(self) -> bool:
        return _admits_none(self.alias)

    @property
    def target(self) -> TypeNode:
        return _with_meta(_expand_alias(self.alias, self.args), self.constraints)


@dataclass(frozen=True, eq=False)
class TypeVarNode(TypeNode):
    pass


@dataclass(frozen=True, eq=False)
class ForwardRefNode(TypeNode):
    name: str


def parse(annotation: Any, constraints: Constraints | None = None) -> TypeNode:
    """Parse an annotation into a type node.

    :param annotation: A type annotation.
    :param constraints: Field level constraints that are not part of the annotation (e.g. pydantic ``Field(ge=1)``).

    :returns: A type node.
    """
    # Fast path, by identity: factories parse the same annotation objects on every build. `get_type_hints` does
    # rebuild builtin generics such as `list[int]` each time, but their origin and arguments are the same objects, so
    # those are looked up by the identities of their parts.
    is_builtin_generic = type(annotation) is GenericAlias
    key: Any = (id(annotation.__origin__), *map(id, annotation.__args__)) if is_builtin_generic else id(annotation)
    # The objects are kept alive in the cache, so no other object can have their ids: a hit is always the same object.
    if (cached := _parsed_by_identity.get(key)) is not None:
        node = cached[1]
    else:
        parts = (annotation.__origin__, *annotation.__args__) if is_builtin_generic else (annotation,)
        try:
            node = _parse_cached(_cache_key(annotation))
        except TypeError:  # unhashable, e.g. `Annotated` with dict metadata
            node = _parse(annotation)
        if len(_parsed_by_identity) >= _MAX_CACHED:
            _parsed_by_identity.clear()
        _parsed_by_identity[key] = (parts, node)
    return _with_meta(node, constraints) if constraints else node


_MAX_CACHED = 4096
_parsed_by_identity: dict[Any, tuple[tuple[Any, ...], TypeNode]] = {}


def _cache_key(annotation: Any) -> tuple[Any, tuple[Any, ...]]:
    """Return a cache key for an annotation that, unlike its equality, depends on the order of union members."""
    return annotation, tuple(_cache_key(arg) for arg in get_args(annotation))


@functools.lru_cache(maxsize=_MAX_CACHED)
def _parse_cached(key: tuple[Any, tuple[Any, ...]]) -> TypeNode:
    return _parse(key[0])


def _parse(tp: Any) -> TypeNode:  # noqa: PLR0911, PLR0912, C901
    if tp is Any:
        return AnyNode(raw=tp, constraints=None)
    if tp is None or tp is NoneType:
        return NoneNode(raw=tp, constraints=None)
    if isinstance(tp, str):
        return ForwardRefNode(raw=tp, constraints=None, name=tp)
    if isinstance(tp, ForwardRef):
        return ForwardRefNode(raw=tp, constraints=None, name=tp.__forward_arg__)
    if isinstance(tp, TypeVar):
        return TypeVarNode(raw=tp, constraints=None)
    if is_type_alias(tp):
        return AliasNode(raw=tp, constraints=None, alias=tp, args=())
    if is_new_type(tp):
        return NewTypeNode(raw=tp, constraints=None, supertype=parse(tp.__supertype__))

    origin, args = get_origin(tp), get_args(tp)

    if origin in _QUALIFIERS:
        return parse(args[0])
    if origin is Annotated:
        constraints = parse_constraints(_flatten_metadata(args[1:]))
        return replace(_with_meta(parse(args[0]), constraints or None), raw=tp)
    if origin in UNION_TYPES:
        return make_union(tp, [parse(arg) for arg in args])
    if origin is Literal:
        return LiteralNode(raw=tp, constraints=None, values=args)
    if is_type_alias(origin):
        return AliasNode(raw=tp, constraints=None, alias=origin, args=args)

    cls = _concrete(origin or tp)
    if isinstance(cls, type) and not issubclass(cls, (str, bytes, bytearray)) and not _is_record(cls):
        if issubclass(cls, tuple):
            variadic = not args or (len(args) == 2 and args[1] is Ellipsis)  # noqa: PLR2004
            items = (parse(args[0]) if args else _ANY,) if variadic else tuple(parse(arg) for arg in args)
            return TupleNode(raw=tp, constraints=None, cls=cls, items=items, variadic=variadic)
        if issubclass(cls, abc.Mapping):
            key, value = (parse(args[0]), parse(args[1])) if len(args) == 2 else (_ANY, _ANY)  # noqa: PLR2004
            return MappingNode(raw=tp, constraints=None, cls=cls, key=key, value=value)
        if issubclass(cls, (abc.Collection, deque)):
            item = parse(args[0]) if args else _ANY
            return CollectionNode(raw=tp, constraints=None, cls=cls, item=item)

    return InstanceNode(raw=tp, constraints=None, cls=cls)


_ANY = AnyNode(raw=Any, constraints=None)


def make_union(raw: Any, members: list[TypeNode]) -> TypeNode:
    """Build a union: flatten nested unions, keep a single ``None`` member, and unwrap single member unions.

    :param raw: The annotation the union was written as.
    :param members: The parsed members.

    :returns: A ``UnionNode``, or the only member.
    """
    flat: list[TypeNode] = []
    for member in members:
        for item in member.members if isinstance(member, UnionNode) and not member.constraints else (member,):
            if not (isinstance(item, NoneNode) and any(isinstance(existing, NoneNode) for existing in flat)):
                flat.append(item)

    if len(flat) == 1:
        return flat[0]
    return UnionNode(raw=raw, constraints=None, members=tuple(flat))


def with_children(node: TypeNode, children: list[TypeNode]) -> TypeNode:
    """Rebuild a node from child nodes given explicitly by a model integration.

    Some integrations attach constraints to ``FieldMeta.children`` rather than to the annotation (pydantic puts each
    union member's constraints on its child), so those children are the source of truth for the node's members.

    :param node: The node parsed from the field's annotation.
    :param children: The parsed child field metas: a union's members other than ``None``, or a container's item,
        key/value or element types.

    :returns: The rebuilt node.
    """
    if not children:
        return node
    if isinstance(node, UnionNode):
        # Swap each member other than `None` for its child, keeping `None` where it was written.
        replacements = iter(children)
        members = [member if isinstance(member, NoneNode) else next(replacements, None) for member in node.members]
        if None in members or next(replacements, None) is not None:  # the children don't line up with the members
            members = [*children, *(member for member in node.members if isinstance(member, NoneNode))]
        return make_union(node.raw, cast("list[TypeNode]", members))
    if isinstance(node, CollectionNode):
        return replace(node, item=children[0])
    if isinstance(node, MappingNode) and len(children) == 2:  # noqa: PLR2004
        return replace(node, key=children[0], value=children[1])
    if isinstance(node, TupleNode):
        return replace(node, items=tuple(children[:1] if node.variadic else children))
    return node


def _with_meta(node: TypeNode, constraints: Constraints | None) -> TypeNode:
    """Attach constraints to a node, returning the node itself if they are already attached.

    Constraints on a union apply to each member, so ``Annotated[int | None, Ge(1)]`` constrains the ``int``.
    """
    if not constraints or isinstance(node, (AnyNode, NoneNode, LiteralNode)):
        return node
    if isinstance(node, UnionNode):
        members = tuple(_with_meta(member, constraints) for member in node.members)
        if all(new is old for new, old in zip(members, node.members)):
            return node
        return replace(node, members=members)
    if isinstance(node, NewTypeNode):
        supertype = _with_meta(node.supertype, constraints)
        return node if supertype is node.supertype else replace(node, supertype=supertype)
    # An AliasNode keeps them and applies them to its target when that is resolved.
    existing = cast("dict[str, Any]", node.constraints or {})
    if all(key in existing and existing[key] == value for key, value in constraints.items()):
        return node
    return replace(node, constraints=Frozendict({**existing, **constraints}))  # type: ignore[arg-type]


def _flatten_metadata(metadata: tuple[Any, ...]) -> list[Any]:
    """Pydantic wraps ``Annotated`` metadata in ``FieldInfo``; unwrap it so the constraint objects are parsed."""
    flat: list[Any] = []
    for item in metadata:
        if type(item).__name__ == "FieldInfo" and isinstance(inner := getattr(item, "metadata", None), list):
            flat.extend(inner)
        elif item is not None:
            flat.append(item)
    return flat


def _expand_alias(alias: Any, args: tuple[Any, ...]) -> TypeNode:
    value = alias.__value__
    if (params := getattr(alias, "__type_params__", ())) and args:
        value = _substitute(value, dict(zip(params, args)))
    return parse(value)


def _substitute(tp: Any, substitutions: dict[Any, Any]) -> Any:
    """Replace type variables without expanding nested aliases, so recursive generic aliases stay finite."""
    if isinstance(tp, TypeVar):
        return substitutions.get(tp, tp)
    origin, args = get_origin(tp), get_args(tp)
    if not args or origin in (Literal, abc.Callable):
        return tp
    new_args: tuple[Any, ...] = tuple(_substitute(arg, substitutions) for arg in args)
    if origin is Annotated:
        return Annotated[(new_args[0], *args[1:])]
    if origin in UNION_TYPES:
        return Union[new_args]
    return origin[new_args[0]] if len(new_args) == 1 else origin[new_args]


def _admits_none(alias: Any) -> bool:
    """Whether a type alias's definition admits ``None`` (``type MaybeInt = int | None``).

    Looks only at the top of the definition - through ``Annotated``, qualifiers and other aliases - without parsing
    union members, so it stays finite for recursive aliases.
    """
    seen: set[Any] = set()
    value = alias
    while True:
        origin = get_origin(value)
        if is_type_alias(value) or is_type_alias(origin):
            definition = value if is_type_alias(value) else origin
            if definition in seen:
                return False
            seen.add(definition)
            value = definition.__value__
            continue
        if origin is Annotated or origin in _QUALIFIERS:
            value = get_args(value)[0]
            continue
        if value is None or value is NoneType:
            return True
        return origin in UNION_TYPES and any(arg is None or arg is NoneType for arg in get_args(value))


def _concrete(cls: Any) -> Any:
    """Map an abstract collection type to the concrete type to build: ``Sequence`` -> ``list``, ``Set`` -> ``set``."""
    if (mapped := TYPE_MAPPING.get(cls)) is not None:
        return mapped
    if isinstance(cls, type) and cls.__module__ == "collections.abc":
        if issubclass(cls, abc.Mapping):
            return dict
        if issubclass(cls, abc.Set):
            return set
        if issubclass(cls, abc.Collection):
            return list
    return cls


def _is_record(cls: type) -> bool:
    """Classes built on a container base that are really records: ``TypedDict`` and ``NamedTuple``."""
    return is_typeddict(cls) or (issubclass(cls, tuple) and hasattr(cls, "_fields"))


__all__ = (
    "AliasNode",
    "AnyNode",
    "CollectionNode",
    "ForwardRefNode",
    "InstanceNode",
    "LiteralNode",
    "MappingNode",
    "NewTypeNode",
    "NoneNode",
    "TupleNode",
    "TypeNode",
    "TypeVarNode",
    "UnionNode",
    "make_union",
    "parse",
    "with_children",
)
