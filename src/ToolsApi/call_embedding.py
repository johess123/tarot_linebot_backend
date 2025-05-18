from openai import OpenAI
import os
from dotenv import load_dotenv

# 只在本地開發時載入 .env（避免在 Render 重複讀取）
if os.getenv("RENDER") is None:  # Render 上會內建設定 RENDER=True
    load_dotenv()

openai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
embedding_model = os.getenv("EMBEDDING_MODEL")

def get_embedding(text: str): # 轉向量
    res = openai.embeddings.create(input=text, model=embedding_model)
    return res.data[0].embedding
