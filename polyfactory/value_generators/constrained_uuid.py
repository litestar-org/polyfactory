from typing import Literal, cast
from uuid import NAMESPACE_DNS, UUID, uuid1, uuid3, uuid5

from faker import Faker


def handle_constrained_uuid(uuid_version: Literal[1, 3, 4, 5], faker: Faker) -> UUID:
    if uuid_version == 1:
        return uuid1()
    if uuid_version == 3:
        return uuid3(NAMESPACE_DNS, faker.pystr())
    if uuid_version == 4:
        return cast("UUID", faker.uuid4())
    return uuid5(NAMESPACE_DNS, faker.pystr())
