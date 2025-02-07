from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession

from polyfactory.factories.sqlalchemy_factory import SQLAlchemyFactory
from tests.sqlalchemy_factory.models import Keyword, User, UserKeywordAssociation


class KeywordFactory(SQLAlchemyFactory[Keyword]): ...


def test_association_proxy() -> None:
    class UserFactory(SQLAlchemyFactory[User]):
        __set_association_proxy__ = True

    user = UserFactory.build()
    assert isinstance(user.keywords[0], Keyword)
    assert isinstance(user.user_keyword_associations[0], UserKeywordAssociation)


async def test_async_persistence(async_engine: AsyncEngine) -> None:
    async with AsyncSession(async_engine) as session:

        class AsyncUserFactory(SQLAlchemyFactory[User]):
            __set_association_proxy__ = True
            __async_session__ = session

        instance = await AsyncUserFactory.create_async()
        instances = await AsyncUserFactory.create_batch_async(3)

    async with AsyncSession(async_engine) as session:
        result = await session.scalars(select(User))
        assert len(result.all()) == 4

        user = await session.get(User, instance.id)
        assert user
        assert isinstance(user.keywords[0], Keyword)
        assert isinstance(user.user_keyword_associations[0], UserKeywordAssociation)

        for instance in instances:
            user = await session.get(User, instance.id)
            assert user
            assert isinstance(user.keywords[0], Keyword)
            assert isinstance(user.user_keyword_associations[0], UserKeywordAssociation)
