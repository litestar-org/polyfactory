from __future__ import annotations

from sqlalchemy import ForeignKey
from sqlalchemy.ext.associationproxy import AssociationProxy, association_proxy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from polyfactory.factories.sqlalchemy_factory import SQLAlchemyFactory


class Base(DeclarativeBase): ...


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]

    user_keyword_associations: Mapped[list["UserKeywordAssociation"]] = relationship(
        back_populates="user",
    )
    keywords: AssociationProxy[list["Keyword"]] = association_proxy(
        "user_keyword_associations",
        "keyword",
        creator=lambda keyword_obj: UserKeywordAssociation(keyword=keyword_obj),
    )


class UserKeywordAssociation(Base):
    __tablename__ = "user_keyword"
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    keyword_id: Mapped[int] = mapped_column(ForeignKey("keywords.id"), primary_key=True)

    user: Mapped[User] = relationship(back_populates="user_keyword_associations")
    keyword: Mapped["Keyword"] = relationship()


class Keyword(Base):
    __tablename__ = "keywords"
    id: Mapped[int] = mapped_column(primary_key=True)
    keyword: Mapped[str]


class UserFactory(SQLAlchemyFactory[User]): ...


class UserFactoryWithAssociation(SQLAlchemyFactory[User]):
    __set_association_proxy__ = True


def test_sqla_factory() -> None:
    user = UserFactory.build()
    assert not user.user_keyword_associations
    assert not user.keywords


def test_sqla_factory_with_association() -> None:
    user = UserFactoryWithAssociation.build()
    assert isinstance(user.user_keyword_associations[0], UserKeywordAssociation)
    assert isinstance(user.keywords[0], Keyword)
