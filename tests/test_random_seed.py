from pydantic import BaseModel, Field

from pydantic_factories import ModelFactory


def test_random_seed() -> None:
    class MyModel(BaseModel):
        id: int
        special_id: str = Field(regex=r"ID-[1-9]{3}\.[1-9]{3}")

    class MyModelFactory(ModelFactory):
        __model__ = MyModel

    ModelFactory.seed_random(1651)

    ins = MyModelFactory.build()

    assert ins.id == 4
    assert ins.special_id == "ID-515.943"
