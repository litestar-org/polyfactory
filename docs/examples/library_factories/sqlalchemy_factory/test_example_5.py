import datetime
from typing import Any, Callable, Dict

from sqlalchemy import types
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from polyfactory.factories.sqlalchemy_factory import SQLAlchemyFactory


class CustomType(types.UserDefinedType):
    ...


class Base(DeclarativeBase):
    ...


class Author(Base):
    __tablename__ = "authors"

    id: Mapped[int] = mapped_column(primary_key=True)
    first_publication_at: Mapped[Any] = mapped_column(type_=CustomType())


class AuthorFactory(SQLAlchemyFactory[Author]):
    __model__ = Author

    @classmethod
    def get_sqlalchemy_types(cls) -> Dict[Any, Callable[[], Any]]:
        return {**super().get_sqlalchemy_types(), CustomType: lambda: cls.__faker__.date_time()}


def test_sqla_user_defined_type_custom_type_factory() -> None:
    author = AuthorFactory.build()
    assert isinstance(author.first_publication_at, datetime.datetime)
