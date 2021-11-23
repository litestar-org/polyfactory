import pytest
from motor.motor_asyncio import AsyncIOMotorClient

# mongo can be ran locally or using the docker-compose file at the repository's root
mongo_dsn = "mongodb://localhost:27017"


@pytest.fixture(scope="function")
def mongo_connection():
    return AsyncIOMotorClient(mongo_dsn)
