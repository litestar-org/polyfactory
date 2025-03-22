from __future__ import annotations

from collections.abc import Callable
from decimal import Decimal
from typing import Any

from sqlalchemy import types
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from polyfactory.factories.sqlalchemy_factory import SQLAlchemyFactory


class Location(types.TypeEngine):
    cache_ok = True


class Base(DeclarativeBase): ...


class Place(Base):
    __tablename__ = "location"

    id: Mapped[int] = mapped_column(primary_key=True)
    location: Mapped[tuple[Decimal, Decimal]] = mapped_column(Location)


class PlaceFactory(SQLAlchemyFactory[Place]):
    @classmethod
    def get_sqlalchemy_types(cls) -> dict[Any, Callable[[], Any]]:
        mapping = super().get_sqlalchemy_types()
        mapping[Location] = cls.__faker__.latlng
        return mapping


def test_custom_sqla_factory() -> None:
    result = PlaceFactory.build()
    assert isinstance(result.location, tuple)
