from random import Random, randint
from typing import Optional

import pytest
from faker import Faker

from pydantic import VERSION, BaseModel, Field

from polyfactory.factories.pydantic_factory import ModelFactory
from polyfactory.fields import Use


def test_random_seed() -> None:
    class MyModel(BaseModel):
        id: int
        special_id: str = (
            Field(pattern=r"ID-[1-9]{3}\.[1-9]{3}")
            if VERSION.startswith("2")
            else Field(regex=r"ID-[1-9]{3}\.[1-9]{3}")  # type: ignore[call-overload]
        )

    class MyModelFactory(ModelFactory):
        __model__ = MyModel

    ModelFactory.seed_random(1651)

    ins = MyModelFactory.build()

    assert ins.id == 4
    assert ins.special_id == "ID-515.943"


def test_deterministic_optionals_seeding() -> None:
    class ModelWithOptionalValues(BaseModel):
        name: Optional[str]

    class FactoryWithNoneOptionals(ModelFactory):
        __model__ = ModelWithOptionalValues

    seed = randint(0, 1000)

    ModelFactory.seed_random(seed)
    first_build = [FactoryWithNoneOptionals.build() for _ in range(10)]
    ModelFactory.seed_random(seed)
    second_build = [FactoryWithNoneOptionals.build() for _ in range(10)]
    assert first_build == second_build


def test_deterministic_constrained_strings() -> None:
    class MyModel(BaseModel):
        id: int
        special_id: str = Field(min_length=10, max_length=24)

    class MyModelFactory(ModelFactory):
        __model__ = MyModel

    ModelFactory.seed_random(1651)

    ins = MyModelFactory.build()

    assert ins.id == 4
    assert ins.special_id == "48489ab53c59b24acfe1"


@pytest.mark.parametrize("seed", [0, 1651])
def test_seed_random_controls_previously_bound_use(seed: int, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(ModelFactory, "__random__", Random(42))
    monkeypatch.setattr(ModelFactory, "__faker__", Faker())

    class MyModel(BaseModel):
        value: int

    class MyFactory(ModelFactory[MyModel]):
        value = Use(ModelFactory.__random__.randint, 0, 2**31 - 1)

    expected_random = Random(seed)
    expected = [MyModel(value=expected_random.randint(0, 2**31 - 1)) for _ in range(5)]

    ModelFactory.seed_random(seed)
    assert [MyFactory.build() for _ in range(5)] == expected

    ModelFactory.seed_random(seed)
    assert [MyFactory.build() for _ in range(5)] == expected


def test_seed_random_preserves_configured_random_instance() -> None:
    class CustomRandom(Random):
        pass

    generator = CustomRandom(42)

    class MyModel(BaseModel):
        value: int

    class MyFactory(ModelFactory[MyModel]):
        __random__ = generator
        __faker__ = Faker()
        value = Use(generator.randrange, 2**31)

    expected_random = Random(1651)
    expected = [MyModel(value=expected_random.randrange(2**31)) for _ in range(5)]

    MyFactory.seed_random(1651)
    assert MyFactory.__random__ is generator
    assert [MyFactory.build() for _ in range(5)] == expected

    MyFactory.seed_random(1651)
    assert [MyFactory.build() for _ in range(5)] == expected


def test_declared_random_seed_does_not_reseed_parent_factory() -> None:
    class MyModel(BaseModel):
        value: int

    class ParentFactory(ModelFactory[MyModel]):
        __random_seed__ = 0
        __faker__ = Faker()

        @classmethod
        def value(cls) -> int:
            return cls.__random__.randrange(2**31)

    expected_parent = Random(0)
    assert ParentFactory.build().value == expected_parent.randrange(2**31)

    class ChildFactory(ParentFactory):
        __random_seed__ = 1651

    assert ParentFactory.build().value == expected_parent.randrange(2**31)
    assert ChildFactory.build().value == Random(1651).randrange(2**31)
