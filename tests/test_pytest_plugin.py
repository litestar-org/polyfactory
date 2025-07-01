import pytest

from pydantic import BaseModel

from polyfactory.exceptions import ParameterException
from polyfactory.factories.pydantic_factory import ModelFactory
from polyfactory.fields import Use
from polyfactory.pytest_plugin import register_fixture
from tests.models import Person, PersonFactoryWithoutDefaults


@register_fixture
class PersonFactoryFixture(PersonFactoryWithoutDefaults):
    """Person Factory Fixture."""


@register_fixture(name="another_fixture")
class AnotherPersonFactoryFixture(PersonFactoryWithoutDefaults):
    """Another Person Factory Fixture."""


def test_fixture_register_decorator(
    person_factory_fixture: PersonFactoryFixture,
) -> None:
    person = person_factory_fixture.build()
    assert isinstance(person, Person)


def test_custom_naming_fixture_register_decorator(
    another_fixture: AnotherPersonFactoryFixture,
) -> None:
    person = another_fixture.build()
    assert isinstance(person, Person)


def test_register_with_function_error() -> None:
    with pytest.raises(ParameterException):

        @register_fixture  # type: ignore
        def foo() -> None:
            pass


def test_register_with_class_not_model_factory_error() -> None:
    with pytest.raises(ParameterException):

        @register_fixture
        class Foo:  # type: ignore[type-var]
            pass


class MyModel(BaseModel):
    best_friend: Person
    all_friends: list[Person]
    enemies: list[Person]


def test_using_factory_directly() -> None:
    class MyFactory(ModelFactory[MyModel]):
        __model__ = MyModel

        best_friend = Use(PersonFactoryFixture.build, name="mike")
        all_friends = Use(PersonFactoryFixture.batch, size=5)
        enemies = Use(PersonFactoryFixture.batch, size=0)

    result = MyFactory.build()
    assert result.best_friend.name == "mike"
    assert len(result.all_friends) == 5
    assert result.enemies == []
