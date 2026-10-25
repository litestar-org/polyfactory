import typing
from collections import abc, deque
from collections.abc import Sequence
from typing import (
    Annotated,
    Any,
    Callable,
    ClassVar,
    ForwardRef,
    Literal,
    NamedTuple,
    NewType,
    Optional,
    TypeVar,
    Union,
)

import pytest
from annotated_types import Ge, Le, Len
from typing_extensions import NotRequired, Required, TypeAliasType, TypedDict

from pydantic import BaseModel, Field

from polyfactory.factories.pydantic_factory import _IS_PYDANTIC_V1, ModelFactory
from polyfactory.field_meta import FieldMeta
from polyfactory.utils._internal.type_node import (
    AliasNode,
    AnyNode,
    CollectionNode,
    ForwardRefNode,
    InstanceNode,
    LiteralNode,
    MappingNode,
    NewTypeNode,
    NoneNode,
    TupleNode,
    TypeVarNode,
    UnionNode,
    make_union,
    parse,
)

T = TypeVar("T")

Name = TypeAliasType("Name", Annotated[str, Len(1, 5)])
Json = TypeAliasType("Json", Union[None, int, str, list["Json"], dict[str, "Json"]])  # type: ignore[misc]
MaybeList = TypeAliasType("MaybeList", Optional[list[T]], type_params=(T,))
MaybeInt = TypeAliasType("MaybeInt", Optional[int])
AnnotatedMaybeInt = TypeAliasType("AnnotatedMaybeInt", Annotated[Optional[int], Ge(1)])
AliasOfMaybeInt = TypeAliasType("AliasOfMaybeInt", MaybeInt)


def test_leaf_kinds() -> None:
    assert isinstance(parse(Any), AnyNode)
    assert isinstance(parse(None), NoneNode)
    assert isinstance(parse(T), TypeVarNode)
    assert isinstance(parse(Callable[[int], str]), InstanceNode)

    node = parse(int)
    assert isinstance(node, InstanceNode)
    assert node.cls is int
    assert not node.allows_none
    assert node.constraints is None


@pytest.mark.parametrize("annotation", ("Model", ForwardRef("Model")))
def test_forward_ref(annotation: Any) -> None:
    node = parse(annotation)
    assert isinstance(node, ForwardRefNode)
    assert node.name == "Model"


def test_optional_is_a_union_with_none() -> None:
    node = parse(Optional[int])
    assert isinstance(node, UnionNode)
    assert node.is_union
    assert node.is_optional
    assert node.allows_none
    assert [type(member) for member in node.members] == [InstanceNode, NoneNode]

    inner = node.strip_optional()
    assert isinstance(inner, InstanceNode)
    assert inner.cls is int


def test_none_position_is_kept() -> None:
    node = parse(Union[None, int, str])
    assert isinstance(node, UnionNode)
    assert [type(member) for member in node.members] == [NoneNode, InstanceNode, InstanceNode]


def test_strip_optional() -> None:
    node = parse(Optional[Union[int, str]]).strip_optional()
    assert isinstance(node, UnionNode)
    assert not node.is_optional
    assert [member.cls for member in node.members] == [int, str]  # type: ignore[attr-defined]
    assert node.raw == Union[int, str]

    plain = parse(int)
    assert plain.strip_optional() is plain


def test_allows_none() -> None:
    assert parse(None).allows_none
    assert not parse(None).is_optional
    assert not parse(Union[int, str]).allows_none
    assert parse(NewType("MaybeId", Optional[int])).allows_none
    assert not parse(NewType("Id", int)).allows_none


def test_make_union_flattens_nested_unions_and_none() -> None:
    inner = parse(Optional[Union[int, str]])
    node = make_union("raw", [inner, parse(bytes), parse(None)])
    assert isinstance(node, UnionNode)
    assert [type(member) for member in node.members] == [InstanceNode, InstanceNode, NoneNode, InstanceNode]

    assert isinstance(make_union("raw", [parse(None)]), NoneNode)


def test_annotated_constraints_attach_to_the_inner_type() -> None:
    annotation = Annotated[list[int], Len(2, 3)]
    node = parse(annotation)
    assert isinstance(node, CollectionNode)
    assert node.cls is list
    assert node.constraints == {"min_length": 2, "max_length": 3}
    assert node.raw is annotation


@pytest.mark.parametrize("annotation", (Annotated[Optional[int], Ge(1)], Optional[Annotated[int, Ge(1)]]))
def test_constraints_on_optional_reach_the_non_none_member(annotation: Any) -> None:
    node = parse(annotation)
    assert node.is_optional
    inner = node.strip_optional()
    assert isinstance(inner, InstanceNode)
    assert inner.constraints == {"ge": 1}


def test_constraints_on_union_apply_to_each_member() -> None:
    node = parse(Annotated[Union[int, float], Ge(1)])
    assert isinstance(node, UnionNode)
    assert [member.constraints for member in node.members] == [{"ge": 1}, {"ge": 1}]


def test_nested_annotated_constraints_merge() -> None:
    node = parse(Annotated[Annotated[int, Ge(1)], Le(5)])
    assert node.constraints == {"ge": 1, "le": 5}


def test_field_constraints_are_merged() -> None:
    node = parse(Annotated[int, Ge(1)], {"le": 5})
    assert node.constraints == {"ge": 1, "le": 5}


def test_constraints_cannot_be_mutated() -> None:
    node = parse(Annotated[int, Ge(1)])
    with pytest.raises(TypeError):
        node.constraints.pop("ge")  # type: ignore[union-attr]


@pytest.mark.parametrize(
    ("annotation", "expected"),
    (
        (list[int], list),
        (typing.List[int], list),  # noqa: UP006
        (typing.Sequence[int], list),
        (Sequence[int], list),
        (abc.Sequence[int], list),
        (abc.MutableSequence[int], list),
        (abc.Collection[int], list),
        (set[int], set),
        (typing.Set[int], set),  # noqa: UP006
        (abc.Set[int], set),
        (abc.MutableSet[int], set),
        (frozenset[int], frozenset),
        (deque[int], deque),
        (Optional[Sequence[int]], list),
    ),
)
def test_collections_map_to_a_concrete_type(annotation: Any, expected: type) -> None:
    node = parse(annotation).strip_optional()
    assert isinstance(node, CollectionNode)
    assert node.cls is expected
    assert isinstance(node.item, InstanceNode)
    assert node.item.cls is int


@pytest.mark.parametrize("annotation", (dict[str, int], abc.Mapping[str, int], abc.MutableMapping[str, int]))
def test_mapping(annotation: Any) -> None:
    node = parse(annotation)
    assert isinstance(node, MappingNode)
    assert node.cls is dict
    assert (node.key.cls, node.value.cls) == (str, int)  # type: ignore[attr-defined]


@pytest.mark.parametrize("annotation", (list, dict, tuple))
def test_bare_containers_have_any_items(annotation: Any) -> None:
    node = parse(annotation)
    children = [getattr(node, name, None) for name in ("item", "key", "value")] + list(getattr(node, "items", ()))
    assert all(isinstance(child, AnyNode) for child in children if child is not None)


def test_tuples() -> None:
    variadic = parse(tuple[int, ...])
    assert isinstance(variadic, TupleNode)
    assert variadic.variadic
    assert [item.cls for item in variadic.items] == [int]  # type: ignore[attr-defined]

    fixed = parse(tuple[int, str])
    assert isinstance(fixed, TupleNode)
    assert not fixed.variadic
    assert [item.cls for item in fixed.items] == [int, str]  # type: ignore[attr-defined]


def test_literal_has_values() -> None:
    node = parse(Literal[1, "a"])
    assert isinstance(node, LiteralNode)
    assert node.values == (1, "a")


def test_strings_and_records_are_not_containers() -> None:
    class Point(NamedTuple):
        x: int

    class TD(TypedDict):
        x: int

    for annotation in (str, bytes, Point, TD):
        node = parse(annotation)
        assert isinstance(node, InstanceNode)
        assert node.cls is annotation


@pytest.mark.parametrize("qualifier", (Required, NotRequired, ClassVar))
def test_qualifiers_are_stripped(qualifier: Any) -> None:
    node = parse(qualifier[Optional[int]])
    assert node.is_optional
    assert node.strip_optional().cls is int  # type: ignore[attr-defined]


def test_readonly_is_stripped() -> None:
    read_only = pytest.importorskip("typing_extensions").ReadOnly
    assert parse(read_only[int]).cls is int  # type: ignore[attr-defined]


def test_newtype_is_nominal() -> None:
    UserIds = NewType("UserIds", list[int])
    node = parse(UserIds)
    assert isinstance(node, NewTypeNode)
    assert node.raw is UserIds
    assert isinstance(node.supertype, CollectionNode)


def test_constraints_on_newtype_reach_the_supertype() -> None:
    UserId = NewType("UserId", int)
    node = parse(Annotated[UserId, Ge(1)])
    assert isinstance(node, NewTypeNode)
    assert node.supertype.constraints == {"ge": 1}


def test_alias_is_nominal_and_lazy() -> None:
    optional = parse(Optional[Name])
    assert optional.is_optional

    node = optional.strip_optional()
    assert isinstance(node, AliasNode)
    assert node.raw is Name
    assert not node.allows_none

    target = node.target
    assert isinstance(target, InstanceNode)
    assert target.cls is str
    assert target.constraints == {"min_length": 1, "max_length": 5}


def test_alias_nullability_comes_from_its_definition() -> None:
    assert parse(MaybeInt).allows_none
    assert parse(AnnotatedMaybeInt).allows_none
    assert parse(AliasOfMaybeInt).allows_none
    assert parse(Json).allows_none
    assert not parse(Name).allows_none
    assert parse(MaybeList[int]).allows_none
    assert not parse(MaybeList[int]).target.strip_optional().item.allows_none  # type: ignore[attr-defined]


def test_recursive_alias() -> None:
    node = parse(Json)
    assert isinstance(node, AliasNode)

    target = node.target
    assert isinstance(target, UnionNode)
    assert target.is_optional
    assert [type(member) for member in target.members] == [
        NoneNode,
        InstanceNode,
        InstanceNode,
        CollectionNode,
        MappingNode,
    ]


def test_generic_alias_substitution() -> None:
    node = parse(MaybeList[int])
    assert isinstance(node, AliasNode)

    target = node.target
    assert target.is_optional
    collection = target.strip_optional()
    assert isinstance(collection, CollectionNode)
    assert collection.item.cls is int  # type: ignore[attr-defined]


@pytest.mark.parametrize(
    ("annotation", "expected"),
    (
        (Union[None, int], [NoneNode, InstanceNode]),
        (Union[int, None], [InstanceNode, NoneNode]),
        (list[Union[None, int]], [NoneNode, InstanceNode]),
        (list[Union[int, None]], [InstanceNode, NoneNode]),
    ),
)
def test_equal_unions_keep_their_own_member_order(annotation: Any, expected: list[type]) -> None:
    # typing considers each pair equal, so a cache keyed on equality would hand back the other spelling.
    node = parse(annotation)
    union = node.item if isinstance(node, CollectionNode) else node
    assert isinstance(union, UnionNode)
    assert [type(member) for member in union.members] == expected


def test_unhashable_metadata() -> None:
    node = parse(Annotated[int, {"ge": 1}])
    assert node.constraints == {"ge": 1}


# --- FieldMeta._type_node ---------------------------------------------------------------------------------------------------


def test_field_meta_type() -> None:
    field_meta = FieldMeta.from_type(Annotated[Optional[int], Ge(1)], name="x")
    node = field_meta._type_node
    assert node.allows_none
    assert node.strip_optional().constraints == {"ge": 1}
    assert field_meta._type_node is node


def test_field_meta_type_keeps_alias_nominal() -> None:
    field_meta = FieldMeta.from_type(Name, name="x")
    assert field_meta.annotation == Annotated[str, Len(1, 5)]  # existing behaviour: from_type expands aliases
    assert isinstance(field_meta._type_node, AliasNode)


def test_field_meta_type_follows_reassignment() -> None:
    field_meta = FieldMeta.from_type(int, name="x")
    assert field_meta._type_node.cls is int  # type: ignore[attr-defined]

    field_meta.annotation = str
    assert field_meta._type_node.cls is str  # type: ignore[attr-defined]

    field_meta.constraints = {"min_length": 1}
    assert field_meta._type_node.constraints == {"min_length": 1}


def test_field_meta_type_uses_explicit_children() -> None:
    child = FieldMeta.from_type(int, constraints={"ge": 1})
    field_meta = FieldMeta(name="x", annotation=Optional[int], children=[child])  # type: ignore[arg-type]
    node = field_meta._type_node
    assert isinstance(node, UnionNode)
    assert [type(member) for member in node.members] == [InstanceNode, NoneNode]
    assert node.strip_optional().constraints == {"ge": 1}


def test_field_meta_type_ignores_derived_children() -> None:
    field_meta = FieldMeta.from_type(list[int], name="x")
    assert field_meta.children
    assert not field_meta._explicit_children


@pytest.mark.skipif(_IS_PYDANTIC_V1, reason="Pydantic 1 keeps these constraints on constrained types")
def test_pydantic_union_constraints_come_from_children() -> None:
    class Model(BaseModel):
        a: Annotated[Optional[int], Field(ge=0, le=10)] = None
        b: Optional[Annotated[str, Field(min_length=2)]] = None
        c: Union[Annotated[int, Field(ge=1)], Annotated[str, Field(max_length=3)]]

    types = {
        field_meta.name: field_meta._type_node for field_meta in ModelFactory.create_factory(Model).get_model_fields()
    }

    assert types["a"].allows_none
    assert types["a"].strip_optional().constraints == {"ge": 0, "le": 10}

    assert types["b"].allows_none
    assert types["b"].strip_optional().constraints == {"min_length": 2}

    assert isinstance(types["c"], UnionNode)
    assert [member.constraints for member in types["c"].members] == [{"ge": 1}, {"max_length": 3}]


def test_pydantic_optional_typing_list_is_one_collection() -> None:
    class Model(BaseModel):
        values: Optional[typing.List[str]]  # noqa: UP006 - the typing spelling is what #895 is about

    (field_meta,) = ModelFactory.create_factory(Model).get_model_fields()
    assert field_meta._type_node.allows_none
    node = field_meta._type_node.strip_optional()
    assert isinstance(node, CollectionNode)
    assert isinstance(node.item, InstanceNode)
    assert node.item.cls is str
