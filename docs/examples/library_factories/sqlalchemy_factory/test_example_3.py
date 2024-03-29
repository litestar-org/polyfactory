from typing import List

from sqlalchemy import ForeignKey, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, relationship

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


class AuthorFactory(SQLAlchemyFactory[Author]):
    __set_relationships__ = True


def test_sqla_factory_persistence() -> None:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    session = Session(engine)

    AuthorFactory.__session__ = session  # Or using a callable that returns a session

    author = AuthorFactory.create_sync()
    assert author.id is not None
    assert author.id == author.books[0].author_id
