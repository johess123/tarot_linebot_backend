from fastapi import APIRouter
from src.service import admin as admin_service
from pydantic import BaseModel
import os

ADMIN_IDS = os.getenv("ADMIN_IDS")

router = APIRouter()

class LoginData(BaseModel):
    userId: str

@router.post("/api/admin/login")
async def login_api(data: LoginData):
    if data.userId in ADMIN_IDS:
        return {"isAdmin": True}
    else:
        return {"isAdmin": False}

class QesAnsData(BaseModel):
    qes: str
    ans: str

@router.post("/api/admin/qes_ans")
async def add_qes_ans_api(data: QesAnsData):
    return await admin_service.add_qes_ans(data.qes, data.ans)

@router.get("/api/admin/qes_ans")
async def get_qes_ans_api():
    return await admin_service.get_qes_ans()

@router.put("/api/admin/qes_ans/{serial_number}")
async def update_qes_ans_api(serial_number: int, data: QesAnsData):
    return await admin_service.update_qes_ans(serial_number, data.qes, data.ans)

@router.delete("/api/admin/qes_ans/{serial_number}")
async def delete_qes_ans_api(serial_number: int):
    return await admin_service.delete_qes_ans(serial_number)