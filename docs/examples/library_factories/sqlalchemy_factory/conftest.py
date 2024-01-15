from collections.abc import Iterable

import pytest

from docs.examples.library_factories.sqlalchemy_factory.test_example_4 import BaseFactory


@pytest.fixture(scope="module")
def _remove_default_factories() -> Iterable[None]:
    yield
    BaseFactory._base_factories.remove(BaseFactory)  # noqa: SLF001
