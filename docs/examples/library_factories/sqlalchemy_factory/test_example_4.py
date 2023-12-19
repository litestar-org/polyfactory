import datetime
from typing import Any

from sqlalchemy import DateTime, types
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from polyfactory.factories.sqlalchemy_factory import SQLAlchemyFactory


class TZAwareDateTime(types.TypeDecorator):
    impl = DateTime(timezone=True)


class Base(DeclarativeBase):
    ...


class Author(Base):
    __tablename__ = "authors"

    id: Mapped[int] = mapped_column(primary_key=True)
    first_publication_at: Mapped[Any] = mapped_column(type_=TZAwareDateTime(), nullable=False)


class AuthorFactory(SQLAlchemyFactory[Author]):
    __model__ = Author


def test_sqla_type_decorator_custom_type_factory() -> None:
    author = AuthorFactory.build()
    assert isinstance(author.first_publication_at, datetime.datetime)
