from fastapi import APIRouter
from src.service import admin as admin_service
from pydantic import BaseModel
import os
from dotenv import load_dotenv
from src.logger import logger

# 只在本地開發時載入 .env（避免在 Render 重複讀取）
if os.getenv("RENDER") is None:  # Render 上會內建設定 RENDER=True
    load_dotenv()

ADMIN_IDS = os.getenv("ADMIN_IDS")

router = APIRouter()

class LoginData(BaseModel):
    userId: str

@router.post("/api/admin/login") # 登入
async def login_api(data: LoginData):
    admin_ids = ADMIN_IDS.split(",") if ADMIN_IDS else []
    logger.info(f"使用者登入 line id: {data.userId}")
    if data.userId in admin_ids:
        return {"isAdmin": True}
    else:
        return {"isAdmin": False}

class QesAnsData(BaseModel):
    qes: str
    ans: str

@router.post("/api/admin/qes_ans") # 新增 Q&A
async def add_qes_ans_api(data: QesAnsData):
    return await admin_service.add_qes_ans(data.qes, data.ans)

@router.get("/api/admin/qes_ans") # 取得 Q&A
async def get_qes_ans_api():
    return await admin_service.get_qes_ans()

@router.put("/api/admin/qes_ans/{serial_number}") # 更新 Q&A
async def update_qes_ans_api(serial_number: int, data: QesAnsData):
    return await admin_service.update_qes_ans(serial_number, data.qes, data.ans)

@router.delete("/api/admin/qes_ans/{serial_number}") # 刪除 Q&A
async def delete_qes_ans_api(serial_number: int):
    return await admin_service.delete_qes_ans(serial_number)

class AnnouncementData(BaseModel):
    announcement: str
    tone: str

@router.post("/api/admin/announcement") # 生成公告
async def generate_announcement(data: AnnouncementData):
    return await admin_service.generate_announcement(data.announcement, data.tone)