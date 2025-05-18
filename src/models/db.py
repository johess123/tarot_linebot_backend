from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

# 只在本地開發時載入 .env（避免在 Render 重複讀取）
if os.getenv("RENDER") is None:  # Render 上會內建設定 RENDER=True
    load_dotenv()

async def get_db(): # 連接 mongodb
    mongo_db_url = os.getenv("MONGO_DB_URL")
    mongo_db_name = os.getenv("MONGO_DB_NAME")
    client = AsyncIOMotorClient(mongo_db_url)
    mongo_db_client = client[mongo_db_name]
    return mongo_db_client