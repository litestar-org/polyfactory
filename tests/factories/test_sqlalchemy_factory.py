from sqlalchemy import Column, types
from sqlalchemy.orm import DeclarativeBase, declared_attr
from sqlalchemy.sql import schema

from polyfactory.factories.sqlalchemy_factory import SQLAlchemyFactory


class SQLAlchemyBaseModel(DeclarativeBase):
    @declared_attr.directive
    def __tablename__(cls) -> str:
        return f"{cls.__name__}"


def test_plain_integer() -> None:
    class MyModel(SQLAlchemyBaseModel):
        id_ = Column(types.Integer, primary_key=True)

    class MyModelFactory(SQLAlchemyFactory[MyModel]):
        __model__ = MyModel

    result = MyModelFactory.build()

    assert result is not None
    assert isinstance(result.id_, int)  # type: ignore


def test_default_factory() -> None:
    default_id = -40
    default_string = "default_string"

    class MyModel(SQLAlchemyBaseModel):
        id_ = Column(types.Integer, default=lambda: default_id, primary_key=True)
        name = Column(types.String, schema.ColumnDefault(default_string))

    class MyModelFactory(SQLAlchemyFactory[MyModel]):
        __model__ = MyModel

    result = MyModelFactory.build()

    assert result is not None
    assert result.id_ == default_id
    assert result.name == default_string
