from typing import Optional

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship
from sqlalchemy.orm.decl_api import DeclarativeMeta, registry

from polyfactory.factories.sqlalchemy_factory import SQLAlchemyFactory

_registry = registry()


class Base(metaclass=DeclarativeMeta):
    __abstract__ = True
    __allow_unmapped__ = True

    registry = _registry
    metadata = _registry.metadata


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String)

    user_keyword_associations = relationship(
        "UserKeywordAssociation",
        back_populates="user",
    )
    keywords = association_proxy(
        "user_keyword_associations", "keyword", creator=lambda keyword_obj: UserKeywordAssociation(keyword=keyword_obj)
    )


class UserKeywordAssociation(Base):
    __tablename__ = "user_keyword"

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    keyword_id = Column(Integer, ForeignKey("keywords.id"), primary_key=True)

    user = relationship(User, back_populates="user_keyword_associations")
    keyword = relationship("Keyword")

    # for prevent mypy error: Unexpected keyword argument "keyword" for "UserKeywordAssociation"  [call-arg]
    def __init__(self, keyword: Optional["Keyword"] = None):
        self.keyword = keyword


class Keyword(Base):
    __tablename__ = "keywords"

    id = Column(Integer, primary_key=True)
    keyword = Column(String)


def test_association_proxy() -> None:
    class UserFactory(SQLAlchemyFactory[User]):
        __set_association_proxy__ = True

    user = UserFactory.build()
    assert isinstance(user.keywords[0], Keyword)
    assert isinstance(user.user_keyword_associations[0], UserKeywordAssociation)


def test_complex_association_proxy() -> None:
    class KeywordFactory(SQLAlchemyFactory[Keyword]): ...

    class ComplexUserFactory(SQLAlchemyFactory[User]):
        __set_association_proxy__ = True

        keywords = KeywordFactory.batch(3)

    user = ComplexUserFactory.build()
    assert isinstance(user, User)
    assert isinstance(user.keywords[0], Keyword)
    assert len(user.keywords) == 3
    assert isinstance(user.user_keyword_associations[0], UserKeywordAssociation)
    assert len(user.user_keyword_associations) == 3
