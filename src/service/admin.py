from src.models import admin as admin_model
from src.ToolsApi.call_embedding import get_embedding

async def add_qes_ans(qes: str, ans: str):
    qes_embedding = get_embedding(qes)
    ans_embedding = get_embedding(ans)
    await admin_model.insert_qes_ans(qes, qes_embedding, ans, ans_embedding)
    return {"ok": True}

async def get_qes_ans():
    return await admin_model.get_qes_ans()

async def update_qes_ans(serial_number: int, qes: str, ans: str):
    qes_embedding = get_embedding(qes)
    ans_embedding = get_embedding(ans)
    return await admin_model.update_qes_ans(serial_number, qes, qes_embedding, ans, ans_embedding)

async def delete_qes_ans(serial_number: int):
    return await admin_model.delete_qes_ans(serial_number)