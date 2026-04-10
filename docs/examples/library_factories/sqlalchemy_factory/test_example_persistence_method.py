from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from polyfactory.factories.sqlalchemy_factory import SQLAlchemyFactory, SQLAlchemyPersistenceMethod


class Base(DeclarativeBase): ...


class Author(Base):
    __tablename__ = "authors"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]


class AuthorFactory(SQLAlchemyFactory[Author]):
    __set_relationships__ = True
    __persistence_method__ = SQLAlchemyPersistenceMethod.FLUSH
