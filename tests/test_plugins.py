from pydantic_factories.plugins.pytest_plugin import register_fixture
from tests.models import PersonFactoryWithoutDefaults


@register_fixture
class PersonFactoryFixture(PersonFactoryWithoutDefaults):
    ...


@register_fixture(name="another_fixutre")
class AnotherPersonFactoryFixture(PersonFactoryWithoutDefaults):
    ...


def test_fixture_register_decorator(person_factory_fixture: PersonFactoryWithoutDefaults) -> None:
    person = person_factory_fixture.build()
    assert isinstance(person, PersonFactoryWithoutDefaults.__model__)


def test_custom_naming_fixture_register_decorator(another_fixutre: PersonFactoryWithoutDefaults) -> None:
    person = another_fixutre.build()
    assert isinstance(person, PersonFactoryWithoutDefaults.__model__)
