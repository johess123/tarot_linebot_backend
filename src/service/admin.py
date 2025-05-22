from src.models import admin as admin_model
from src.ToolsApi import call_llm, call_embedding
from src.config.prompt import tone
from datetime import date

async def add_qes_ans(qes: str, ans: str): # 新增 Q&A
    qes_embedding = call_embedding.get_embedding(qes)
    ans_embedding = call_embedding.get_embedding(ans)
    await admin_model.insert_qes_ans(qes, qes_embedding, ans, ans_embedding)
    return {"ok": True}

async def get_qes_ans(): # 取得 Q&A
    return await admin_model.get_qes_ans()

async def update_qes_ans(serial_number: int, qes: str, ans: str): # 更新 Q&A
    qes_embedding = call_embedding.get_embedding(qes)
    ans_embedding = call_embedding.get_embedding(ans)
    return await admin_model.update_qes_ans(serial_number, qes, qes_embedding, ans, ans_embedding)

async def delete_qes_ans(serial_number: int): # 刪除 Q&A
    return await admin_model.delete_qes_ans(serial_number)

async def generate_announcement(content: str, choose_tone: str): # 生成公告
    text_min_length = round(len(content)*0.8)
    text_max_length = round(len(content)*1.2)
    today = date.today()
    messages = [
        {
            "role": "system",
            "content": tone[choose_tone]["system"]
        },
        {
            "role": "user",
            "content": tone[choose_tone]["constraints"].format(text_min_length=text_min_length, text_max_length=text_max_length, today=today) + tone[choose_tone]["input"].format(input=content)
        }
    ]
    print("messages:", messages)
    result = await call_llm.call_gpt(messages)
    return {"result": result}