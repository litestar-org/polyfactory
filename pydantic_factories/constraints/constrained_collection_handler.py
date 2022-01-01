from typing import TYPE_CHECKING, Any, Union, cast

from pydantic import ConstrainedList, ConstrainedSet
from pydantic.fields import ModelField
from typing_extensions import Type

from pydantic_factories.exceptions import ParameterError
from pydantic_factories.utils import random
from pydantic_factories.value_generators.complex_types import handle_complex_type

if TYPE_CHECKING:  # pragma: no cover
    from pydantic_factories.factory import ModelFactory


def handle_constrained_collection(
    collection_type: Union[Type[list], Type[set]],
    model_factory: Type["ModelFactory"],
    model_field: ModelField,
) -> Union[list, set]:
    """Generate a constrained list or set"""
    constrained_field = cast(Union[ConstrainedList, ConstrainedSet], model_field.outer_type_)
    min_items = constrained_field.min_items or 0
    max_items = constrained_field.max_items if constrained_field.max_items is not None else min_items + 1
    assert max_items >= min_items, "max_items must be longer or equal to min_items"
    if model_field.sub_fields:
        handler = lambda: handle_complex_type(  # noqa: E731
            model_field=random.choice(model_field.sub_fields), model_factory=model_factory
        )
    else:
        t_type = constrained_field.item_type if constrained_field.item_type is not Any else str
        handler = lambda: model_factory.get_mock_value(t_type)  # noqa: E731
    collection: Union[list, set] = collection_type()
    try:
        while len(collection) < random.randint(min_items, max_items):
            value = handler()  # type: ignore
            if isinstance(collection, set):
                collection.add(value)
            else:
                collection.append(value)
        return collection
    except TypeError as e:
        raise ParameterError(f"cannot generate a constrained collection of type: {constrained_field.item_type}") from e
