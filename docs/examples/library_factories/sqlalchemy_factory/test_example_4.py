from typing import List

from sqlalchemy import ForeignKey, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, relationship

from polyfactory.factories.sqlalchemy_factory import SQLAlchemyFactory, T


class Base(DeclarativeBase): ...


class Author(Base):
    __tablename__ = "authors"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]

    books: Mapped[List["Book"]] = relationship(
        "Book",
        uselist=True,
        back_populates="author",
    )


class Book(Base):
    __tablename__ = "books"

    id: Mapped[int] = mapped_column(primary_key=True)
    author_id: Mapped[int] = mapped_column(ForeignKey(Author.id), nullable=False)
    author: Mapped[Author] = relationship(
        "Author",
        uselist=False,
        back_populates="books",
    )


class BaseFactory(SQLAlchemyFactory[T]):
    __is_base_factory__ = True
    __set_relationships__ = True
    __randomize_collection_length__ = True
    __min_collection_length__ = 3


def test_custom_sqla_factory() -> None:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    session = Session(engine)

    BaseFactory.__session__ = session  # Or using a callable that returns a session

    author = BaseFactory.create_factory(Author).create_sync()
    assert author.id is not None
    assert author.id == author.books[0].author_id

    book = BaseFactory.create_factory(Book).create_sync()
    assert book.id is not None
    assert book.author.books == [book]
