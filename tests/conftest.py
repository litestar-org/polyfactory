import pytest
from motor.motor_asyncio import AsyncIOMotorClient

# mongo can be ran locally or using the docker-compose file at the repository's root

mongo_dsn = "mongodb://localhost:27017"
postgres_dsn = "postgresql+asyncpg://pydantic-factories:pydantic-factories@postgres:5432/pydantic-factories"


@pytest.fixture(scope="function")
def mongo_connection():
    return AsyncIOMotorClient(mongo_dsn)
