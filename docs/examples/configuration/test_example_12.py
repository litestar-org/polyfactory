from pydantic import AliasPath, BaseModel, Field

from polyfactory.factories.pydantic_factory import ModelFactory


class User(BaseModel):
    username: str = Field(..., validation_alias="user_name")
    email: str = Field(..., validation_alias=AliasPath("contact", "email"))  # type: ignore[pydantic-alias]


class UserFactory(ModelFactory[User]):
    __by_name__ = True

    # Set factory defaults using field names
    username = "john_doe"


def test_by_name() -> None:
    # Factory uses model_validate with by_name=True
    instance = UserFactory.build()
    assert instance.username == "john_doe"
    assert isinstance(instance.email, str)

    # Can override factory defaults
    instance2 = UserFactory.build(username="jane_doe", email="jane@example.com")
    assert instance2.username == "jane_doe"
    assert instance2.email == "jane@example.com"
