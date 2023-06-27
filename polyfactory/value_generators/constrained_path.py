from os.path import realpath
from pathlib import Path
from typing import Literal, cast

from faker import Faker


# FIXME: remove the pragma when switching to pydantic v2 permanently
def handle_constrained_path(constraint: Literal["file", "dir", "new"], faker: Faker) -> Path:  # pragma: no cover
    if constraint == "new":
        return cast("Path", faker.file_path(depth=1, category=None, extension=None))
    if constraint == "file":
        return Path(realpath(__file__))
    return Path(realpath(__file__)).parent
