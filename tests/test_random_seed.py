from random import randint
from typing import Optional

from pydantic import BaseModel, Field

from polyfactory.factories.pydantic_factory import ModelFactory, pydantic_version


def test_random_seed() -> None:
    class MyModel(BaseModel):
        id: int
        special_id: str = (
            Field(pattern=r"ID-[1-9]{3}\.[1-9]{3}") if pydantic_version == 2 else Field(regex=r"ID-[1-9]{3}\.[1-9]{3}")
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
