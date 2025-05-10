from fastapi import APIRouter, Request, Header, HTTPException
from src.service import chat as chat_service

router = APIRouter()

@router.post("/api/webhook")
async def webhook(request: Request, x_line_signature: str = Header(None)):
    body = await request.body()
    return await chat_service.handle_user_message(body, x_line_signature)
