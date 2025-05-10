from motor.motor_asyncio import AsyncIOMotorClient
import os

async def get_db():
    mongo_db_url = os.getenv("MONGO_DB_URL")
    mongo_db_name = os.getenv("MONGO_DB_NAME")
    client = AsyncIOMotorClient(mongo_db_url)
    mongo_db_client = client[mongo_db_name]
    return mongo_db_client