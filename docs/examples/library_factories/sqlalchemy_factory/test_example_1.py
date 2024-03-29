from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from polyfactory.factories.sqlalchemy_factory import SQLAlchemyFactory


class Base(DeclarativeBase): ...


class Author(Base):
    __tablename__ = "authors"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]


class AuthorFactory(SQLAlchemyFactory[Author]): ...


def test_sqla_factory() -> None:
    author = AuthorFactory.build()
    assert isinstance(author, Author)
