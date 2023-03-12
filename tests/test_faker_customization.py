from faker import Faker

from polyfactory.factories.pydantic_factory import ModelFactory
from tests.models import Pet


def test_allows_user_to_define_faker_instance() -> None:
    my_faker = Faker()
    setattr(my_faker, "__test__attr__", None)

    class MyFactory(ModelFactory):
        __model__ = Pet
        __faker__ = my_faker

    assert hasattr(MyFactory.__faker__, "__test__attr__")
