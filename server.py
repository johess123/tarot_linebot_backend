from fastapi import FastAPI
from src.router import chat as chat_router, admin as admin_router
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI()


frontend_url = os.getenv("FRONTEND_URL")
# 允許的來源
origins = [
    frontend_url,
]

# 加入 CORS 中介層
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, # 允許的來源清單
    allow_credentials=True,
    allow_methods=["*"], # 允許所有方法 (GET, POST, etc.)
    allow_headers=["*"], # 允許所有標頭
)

app.include_router(chat_router.router) # 一般 user
app.include_router(admin_router.router) # admin