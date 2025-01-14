from typing import List

from sqlalchemy import ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from polyfactory.factories.sqlalchemy_factory import SQLAlchemyFactory


class Base(DeclarativeBase): ...


class Author(Base):
    __tablename__ = "authors"

    id: Mapped[int] = mapped_column(primary_key=True)
    books: Mapped[List["Book"]] = relationship("Book", uselist=True)


class Book(Base):
    __tablename__ = "books"

    id: Mapped[int] = mapped_column(primary_key=True)
    author_id: Mapped[int] = mapped_column(ForeignKey(Author.id))


class BookFactory(SQLAlchemyFactory[Book]): ...


class BookFactoryWithForeignKey(SQLAlchemyFactory[Book]):
    __set_foreign_keys__ = True


def test_sqla_factory() -> None:
    book = BookFactory.build()
    assert not book.author_id


def test_sqla_factory_with_foreign_keys() -> None:
    book = BookFactoryWithForeignKey.build()
    assert book.author_id
    assert isinstance(book.author_id, int)
