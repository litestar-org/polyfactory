from typing import Literal, Union

from pydantic import BaseModel, Field
from typing_extensions import Annotated

from pydantic_factories import ModelFactory


def test_discriminated_unions() -> None:
    class BasePet(BaseModel):
        name: str

    class BlackCat(BasePet):
        pet_type: Literal["cat"]
        color: Literal["black"]

    class WhiteCat(BasePet):
        pet_type: Literal["cat"]
        color: Literal["white"]

    class Dog(BasePet):
        pet_type: Literal["dog"]

    class Owner(BaseModel):
        pet: Annotated[
            Union[Annotated[Union[BlackCat, WhiteCat], Field(discriminator="color")], Dog],
            Field(discriminator="pet_type"),
        ]
        name: str

    class OwnerFactory(ModelFactory):
        __model__ = Owner

    assert OwnerFactory.build()
