from src.models.db import get_db
from datetime import datetime

async def query_service_by_vector(embedding): # 取向量相似度最高三個 Q、最高三個 A，再交叉搜尋
    db = await get_db()
    min_score = 0.6
    # 篩出最相近的前 3 筆問題
    qes_pipeline = [
        {
            "$vectorSearch": {
                "index": "vector_index",  # 這裡填你的向量索引名稱
                "queryVector": embedding,
                "path": "embedding_vector",  # 你的欄位名
                "numCandidates": 100,  # 先粗篩 100 筆
                "limit": 3,  # 最後只回傳最接近的 3 筆
                "filter": {
                    "is_deleted": False # 只撈未刪除的問題
                }
            }
        },
        {
            "$project": {
                "_id": 0,
                "content": 1,
                "related_ans": 1,
                "score": 1
            }
        },
    ]
    
    # 問題
    question_cursor = db["question"].aggregate(qes_pipeline)
    question_rows = await question_cursor.to_list(length=3)
    
    ans_pipeline = [
        {
            "$vectorSearch": {
                "index": "vector_index",  # 這裡填你的向量索引名稱
                "queryVector": embedding,
                "path": "embedding_vector",  # 你的欄位名
                "numCandidates": 100,  # 先粗篩 100 筆
                "limit": 3,  # 最後只回傳最接近的 3 筆
                "filter": {
                    "is_deleted": False # 只撈未刪除的答案
                }
            }
        },
        {
            "$project": {
                "_id": 0,
                "content": 1,
                "related_qes": 1,
                "score": 1
            }
        },
    ]

    # 回答
    answer_cursor = db["answer"].aggregate(ans_pipeline)
    answer_rows = await answer_cursor.to_list(length=3)

    # ---------- 建立映射 ----------
    question_map = {q["related_ans"]: q["content"] for q in question_rows if "related_ans" in q}
    answer_map = {a["related_qes"]: a["content"] for a in answer_rows if "related_qes" in a}

    question_ids = set(question_map.keys())
    answer_ids = set(answer_map.keys())

    # 共同有的 id
    common_ids = question_ids & answer_ids
    result = []

    # 先把兩邊都有的組成問答對
    for id_ in common_ids:
        result.append({
            "question": question_map[id_],
            "answer": answer_map[id_]
        })

    # 只在 question 出現的 id
    only_in_question = question_ids - common_ids
    for id_ in only_in_question:
        # 去 answer collection 撈對應 answer（用 serial_number）
        ans_doc = await db["answer"].find_one(
            {"serial_number": id_},
            {"_id": 0, "content": 1}
        )
        if ans_doc:
            result.append({
                "question": question_map[id_],
                "answer": ans_doc["content"]
            })

    # 只在 answer 出現的 id
    only_in_answer = answer_ids - common_ids
    for id_ in only_in_answer:
        # 去 question collection 撈對應 question（用 serial_number）
        qes_doc = await db["question"].find_one(
            {"serial_number": id_},
            {"_id": 0, "content": 1}
        )
        if qes_doc:
            result.append({
                "question": qes_doc["content"],
                "answer": answer_map[id_]
            })

    return result

async def check_user_is_existed(user_id): # 確認 user 是否已經存在
    db = await get_db()
    existing_user = await db["user"].find_one({"user_id": user_id})
    if existing_user: # user 已存在
        return True
    return False


async def add_new_user(user_id, display_name, picture_url): # 新增 user
    db = await get_db()
    user_data = {
        "user_id": user_id,
        "display_name": display_name,
        "picture_url": picture_url,
        "now_chat_mode": "ai",
        "last_chat_mode": "ai",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "change_by": "system",
    }
    await db["user"].insert_one(user_data)

async def get_user_profile(user_id): # 取得使用者資料
    db = await get_db()
    user_profile = await db["user"].find_one({"user_id": user_id})
    return user_profile

async def switch_chat_mode(new_chat_mode, user_id, now_chat_mode, change_by): # 切換客服模式
    db = await get_db()
    user_update = {
        "$set": {
            "now_chat_mode": new_chat_mode,
            "last_chat_mode": now_chat_mode,
            "updated_at": datetime.utcnow(),
            "change_by": change_by
        }
    }
    await db["user"].update_one({"user_id": user_id}, user_update)