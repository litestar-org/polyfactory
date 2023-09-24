import pytest
from sqlalchemy import __version__

if __version__.startswith("1"):
    pytest.skip("SQLA2 required", allow_module_level=True)
