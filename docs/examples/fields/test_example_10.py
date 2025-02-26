from dataclasses import dataclass

from polyfactory.decorators import post_generated
from polyfactory.factories import DataclassFactory
from polyfactory.fields import CallableParam


@dataclass
class Person:
    name: str
    age_next_year: int


class PersonFactoryWithParamValueSpecifiedInFactory(DataclassFactory[Person]):
    """In this factory, the next_years_age_from_calculator must be passed at build time."""

    next_years_age_from_calculator = CallableParam[int](lambda age: age + 1, age=20)

    @post_generated
    @classmethod
    def age_next_year(cls, next_years_age_from_calculator: int) -> int:
        return next_years_age_from_calculator


def test_factory__in_factory() -> None:
    person = PersonFactoryWithParamValueSpecifiedInFactory.build()

    assert isinstance(person, Person)
    assert not hasattr(person, "next_years_age_from_calculator")
    assert person.age_next_year == 21


class PersonFactoryWithParamValueSetAtBuild(DataclassFactory[Person]):
    """In this factory, the next_years_age_from_calculator must be passed at build time."""

    next_years_age_from_calculator = CallableParam[int](age=20)

    @post_generated
    @classmethod
    def age_next_year(cls, next_years_age_from_calculator: int) -> int:
        return next_years_age_from_calculator


def test_factory__build_time() -> None:
    person = PersonFactoryWithParamValueSpecifiedInFactory.build(next_years_age_from_calculator=lambda age: age + 1)

    assert isinstance(person, Person)
    assert not hasattr(person, "next_years_age_from_calculator")
    assert person.age_next_year == 21
