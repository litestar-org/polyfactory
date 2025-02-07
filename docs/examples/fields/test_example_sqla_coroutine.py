from __future__ import annotations

from sqlalchemy import ForeignKey, select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from polyfactory.factories.sqlalchemy_factory import SQLAlchemyFactory

async_engine = create_async_engine("sqlite+aiosqlite:///:memory:")


class Base(DeclarativeBase): ...


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]


class Department(Base):
    __tablename__ = "departments"

    id: Mapped[int] = mapped_column(primary_key=True)
    director_id: Mapped[str] = mapped_column(ForeignKey("users.id"))


class UserFactory(SQLAlchemyFactory[User]): ...


class DepartmentFactory(SQLAlchemyFactory[Department]):
    @classmethod
    async def director_id(cls) -> int:
        async with AsyncSession(async_engine) as session:
            result = (await session.scalars(select(User.id))).all()
            return cls.__random__.choice(result)


async def test_async_coroutine_field() -> None:
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSession(async_engine) as session:
        UserFactory.__async_session__ = session
        await UserFactory.create_batch_async(3)

    async with AsyncSession(async_engine) as session:
        DepartmentFactory.__async_session__ = session
        department = await DepartmentFactory.create_async()
        user = await session.scalar(select(User).where(User.id == department.director_id))
        assert isinstance(user, User)
