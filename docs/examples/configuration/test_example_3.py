from dataclasses import dataclass

from faker import Faker

from polyfactory.factories import DataclassFactory


@dataclass
class Person:
    name: str
    age: float
    height: float
    weight: float


class PersonFactory(DataclassFactory[Person]):
    __faker__ = Faker(locale="es_ES")

    __random_seed__ = 10

    @classmethod
    def name(cls) -> str:
        return cls.__faker__.name()


def test_setting_faker() -> None:
    # the outcome of faker deterministic because we seeded random, and it uses a spanish locale.
    assert PersonFactory.build().name == "Alejandra Romeu-Tolosa"
