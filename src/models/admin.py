from src.models.db import get_db
from datetime import datetime
from bson import ObjectId

async def insert_qes_ans(qes: str, qes_embedding, ans: str, ans_embedding): # 新增 Q&A
    db = await get_db()
    qes_serial_number = await db["question"].count_documents({}) + 1
    ans_serial_number = await db["answer"].count_documents({}) + 1
    question_data = {
        "serial_number": qes_serial_number,
        "content": qes,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "is_deleted": False,
        "related_ans": ans_serial_number,
        "embedding_vector": qes_embedding
    }
    
    answer_data = {
        "serial_number": ans_serial_number,
        "content": ans,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "is_deleted": False,
        "related_qes": qes_serial_number,
        "embedding_vector": ans_embedding
    }
    await db["question"].insert_one(question_data)
    await db["answer"].insert_one(answer_data)

async def get_qes_ans(): # 取得 Q&A
    db = await get_db()
    # 撈出所有尚未刪除的問題與答案
    questions = await db["question"].find({"is_deleted": False}).to_list(length=None)
    answers = await db["answer"].find({"is_deleted": False}).to_list(length=None)

    # 將答案依 serial_number 整理成 dict，方便查找
    answer_dict = {ans["serial_number"]: ans for ans in answers}

    # 對應每個問題找出相關的答案
    result = []
    for qes in questions:
        related_ans = answer_dict.get(qes.get("related_ans"))
        qes["_id"] = str(qes["_id"])  # Convert ObjectId to string
        if related_ans:
            related_ans["_id"] = str(related_ans["_id"])  # Convert ObjectId to string
        result.append({
            "question": qes,
            "answer": related_ans
        })

    return result

async def update_qes_ans(serial_number: int, qes: str, qes_embedding, ans: str, ans_embedding): # 更新 Q&A
    db = await get_db()
    question_update = {
        "$set": {
            "content": qes,
            "updated_at": datetime.utcnow(),
            "embedding_vector": qes_embedding
        }
    }
    answer_update = {
        "$set": {
            "content": ans,
            "updated_at": datetime.utcnow(),
            "embedding_vector": ans_embedding
        }
    }
    await db["question"].update_one({"serial_number": serial_number, "is_deleted": False}, question_update)
    await db["answer"].update_one({"serial_number": serial_number, "is_deleted": False}, answer_update)

async def delete_qes_ans(serial_number: int): # 刪除 Q&A
    db = await get_db()
    question_update = {"$set": {"is_deleted": True, "updated_at": datetime.utcnow()}}
    answer_update = {"$set": {"is_deleted": True, "updated_at": datetime.utcnow()}}
    await db["question"].update_one({"serial_number": serial_number}, question_update)
    await db["answer"].update_one({"serial_number": serial_number}, answer_update)