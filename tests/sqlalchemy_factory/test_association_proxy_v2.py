from typing import List

import pytest
from sqlalchemy import ForeignKey, __version__, orm
from sqlalchemy.ext.associationproxy import AssociationProxy, association_proxy
from sqlalchemy.orm import Mapped, relationship

from polyfactory.factories.sqlalchemy_factory import SQLAlchemyFactory

if __version__.startswith("1"):
    pytest.skip(allow_module_level=True)


class Base(orm.DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = orm.mapped_column(primary_key=True)
    name: Mapped[str]

    user_keyword_associations: Mapped[List["UserKeywordAssociation"]] = relationship(
        back_populates="user",
    )
    keywords: AssociationProxy[List["Keyword"]] = association_proxy(
        "user_keyword_associations",
        "keyword",
        creator=lambda keyword_obj: UserKeywordAssociation(keyword=keyword_obj),
    )


class UserKeywordAssociation(Base):
    __tablename__ = "user_keyword"
    user_id: Mapped[int] = orm.mapped_column(ForeignKey("users.id"), primary_key=True)
    keyword_id: Mapped[int] = orm.mapped_column(ForeignKey("keywords.id"), primary_key=True)

    user: Mapped[User] = relationship(back_populates="user_keyword_associations")
    keyword: Mapped["Keyword"] = relationship()


class Keyword(Base):
    __tablename__ = "keywords"
    id: Mapped[int] = orm.mapped_column(primary_key=True)
    keyword: Mapped[str]


def test_association_proxy() -> None:
    class UserFactory(SQLAlchemyFactory[User]):
        __set_association_proxy__ = True

    user = UserFactory.build()
    assert isinstance(user.keywords[0], Keyword)
    assert isinstance(user.user_keyword_associations[0], UserKeywordAssociation)


async def test_complex_association_proxy() -> None:
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
