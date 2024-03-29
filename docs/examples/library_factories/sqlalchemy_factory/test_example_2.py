from typing import List

from sqlalchemy import ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from polyfactory.factories.sqlalchemy_factory import SQLAlchemyFactory


class Base(DeclarativeBase): ...


class Author(Base):
    __tablename__ = "authors"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]

    books: Mapped[List["Book"]] = relationship("Book", uselist=True)


class Book(Base):
    __tablename__ = "books"

    id: Mapped[int] = mapped_column(primary_key=True)
    author_id: Mapped[int] = mapped_column(ForeignKey(Author.id))


class AuthorFactory(SQLAlchemyFactory[Author]): ...


class AuthorFactoryWithRelationship(SQLAlchemyFactory[Author]):
    __set_relationships__ = True


def test_sqla_factory_without_relationship() -> None:
    author = AuthorFactory.build()
    assert author.books == []


def test_sqla_factory() -> None:
    author = AuthorFactoryWithRelationship.build()
    assert isinstance(author, Author)
    assert isinstance(author.books[0], Book)
