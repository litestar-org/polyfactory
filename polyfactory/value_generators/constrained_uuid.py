from typing import Literal, cast
from uuid import NAMESPACE_DNS, UUID, uuid1, uuid3, uuid5

from faker import Faker


# FIXME: remove the pragma when switching to pydantic v2 permanently
def handle_constrained_uuid(uuid_version: Literal[1, 3, 4, 5], faker: Faker) -> UUID:  # pragma: no cover
    if uuid_version == 1:
        return uuid1()
    if uuid_version == 3:
        return uuid3(NAMESPACE_DNS, faker.pystr())
    if uuid_version == 4:
        return cast("UUID", faker.uuid4())
    return uuid5(NAMESPACE_DNS, faker.pystr())
