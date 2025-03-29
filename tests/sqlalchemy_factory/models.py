from dataclasses import dataclass
from typing import Any, Optional

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    func,
    orm,
    text,
)
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship
from sqlalchemy.orm.decl_api import DeclarativeMeta, registry

_registry = registry()


@dataclass
class NonSQLAchemyClass:
    id: int


class Base(metaclass=DeclarativeMeta):
    __abstract__ = True
    __allow_unmapped__ = True

    registry = _registry
    metadata = _registry.metadata


class Author(Base):
    __tablename__ = "authors"

    id: Any = Column(Integer(), primary_key=True)
    books: Any = orm.relationship(
        "Book",
        collection_class=list,
        uselist=True,
        back_populates="author",
    )


class Book(Base):
    __tablename__ = "books"

    id: Any = Column(Integer(), primary_key=True)
    author_id: Any = Column(
        Integer(),
        ForeignKey(Author.id),
        nullable=False,
    )
    author: Any = orm.relationship(
        Author,
        uselist=False,
        back_populates="books",
    )


class AsyncModel(Base):
    __tablename__ = "async_model"

    id: Any = Column(Integer(), primary_key=True)


class AsyncRefreshModel(Base):
    __tablename__ = "server_default_test"

    id: Any = Column(Integer(), primary_key=True)
    test_datetime: Any = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    test_str: Any = Column(String, nullable=False, server_default=text("test_str"))
    test_int: Any = Column(Integer, nullable=False, server_default=text("123"))
    test_bool: Any = Column(Boolean, nullable=False, server_default=text("False"))


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String)

    user_keyword_associations = relationship(
        "UserKeywordAssociation",
        back_populates="user",
        lazy="selectin",
    )
    keywords = association_proxy(
        "user_keyword_associations", "keyword", creator=lambda keyword_obj: UserKeywordAssociation(keyword=keyword_obj)
    )


class UserKeywordAssociation(Base):
    __tablename__ = "user_keyword"

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    keyword_id = Column(Integer, ForeignKey("keywords.id"), primary_key=True)

    user = relationship(User, back_populates="user_keyword_associations")
    keyword = relationship("Keyword", lazy="selectin")

    # for prevent mypy error: Unexpected keyword argument "keyword" for "UserKeywordAssociation"  [call-arg]
    def __init__(self, keyword: Optional["Keyword"] = None):
        self.keyword = keyword


class Keyword(Base):
    __tablename__ = "keywords"

    id = Column(Integer, primary_key=True)
    keyword = Column(String)


class Department(Base):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True)
    director_id = Column(Integer, ForeignKey("users.id"))
