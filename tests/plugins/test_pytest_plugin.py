import pytest

from pydantic_factories.plugins.pytest_plugin import register_fixture
from tests.models import Person, PersonFactoryWithoutDefaults


@register_fixture
class PersonFactoryFixture(PersonFactoryWithoutDefaults):
    """Person Factory Fixture."""

    ...


@register_fixture(name="another_fixutre")
class AnotherPersonFactoryFixture(PersonFactoryWithoutDefaults):
    """Another Person Factory Fixture."""

    ...


def test_fixture_register_decorator(person_factory_fixture: PersonFactoryWithoutDefaults) -> None:
    person = person_factory_fixture.build()
    assert isinstance(person, Person)


def test_custom_naming_fixture_register_decorator(another_fixutre: AnotherPersonFactoryFixture) -> None:
    person = another_fixutre.build()
    assert isinstance(person, Person)


def test_register_with_function_error() -> None:
    with pytest.raises(ValueError, match="is not a class"):

        @register_fixture  # type: ignore
        def foo() -> None:
            pass


def test_register_with_class_not_model_factory_error() -> None:
    with pytest.raises(ValueError, match="is not a ModelFactory class"):

        @register_fixture  # type: ignore
        class Foo:
            pass
