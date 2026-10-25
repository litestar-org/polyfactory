"""Build and coverage benchmarks.

These run once as ordinary tests in ``pytest tests``. Time them locally with ``make benchmark``; CI tracks them with
CodSpeed, which reports the change on each pull request.
"""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pytest_codspeed import BenchmarkFixture

from pydantic import BaseModel

from polyfactory.factories import DataclassFactory
from polyfactory.factories.pydantic_factory import ModelFactory


@dataclass
class Flat:
    a: int
    b: str
    c: float
    d: bool
    e: bytes
    f: UUID
    g: datetime
    h: Decimal
    i: list[int]
    j: dict[str, int]


class FlatModel(BaseModel):
    a: int
    b: str
    c: float
    d: bool
    e: bytes
    f: UUID
    g: datetime
    h: Decimal
    i: list[int]
    j: dict[str, int]


@dataclass
class Child:
    x: int
    y: str


@dataclass
class Parent:
    """Nested models without a registered factory, so each is built by a dynamically created one."""

    a: int
    child: Child
    maybe_child: Optional[Child]
    children: list[Child]


class ParentModel(BaseModel):
    """Nested dataclasses in a pydantic model, so one build uses more than one kind of factory."""

    a: int
    child: Child
    children: list[Child]


class FlatFactory(DataclassFactory[Flat]):
    __random_seed__ = 1


class FlatModelFactory(ModelFactory[FlatModel]):
    __random_seed__ = 1


class ParentFactory(DataclassFactory[Parent]):
    __random_seed__ = 1


class ParentModelFactory(ModelFactory[ParentModel]):
    __random_seed__ = 1


def test_build_dataclass(benchmark: BenchmarkFixture) -> None:
    benchmark(FlatFactory.build)


def test_build_pydantic(benchmark: BenchmarkFixture) -> None:
    benchmark(FlatModelFactory.build)


def test_build_nested_dataclass(benchmark: BenchmarkFixture) -> None:
    benchmark(ParentFactory.build)


def test_build_nested_pydantic(benchmark: BenchmarkFixture) -> None:
    benchmark(ParentModelFactory.build)


def test_batch_pydantic(benchmark: BenchmarkFixture) -> None:
    benchmark(FlatModelFactory.batch, size=100)


def test_coverage_dataclass(benchmark: BenchmarkFixture) -> None:
    benchmark(lambda: list(FlatFactory.coverage()))


def test_coverage_nested_dataclass(benchmark: BenchmarkFixture) -> None:
    benchmark(lambda: list(ParentFactory.coverage()))
