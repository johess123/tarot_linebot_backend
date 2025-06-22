from src.models import chat as chat_model
from src.ToolsApi import call_llm, rag_tool
from src.config.prompt import rewrite_prompt, chatbot_prompt
from linebot import LineBotApi, WebhookParser
from linebot.models import MessageEvent, TextMessage, TextSendMessage, PostbackEvent, FollowEvent
import os
import uuid
from dotenv import load_dotenv
from src.logger import logger
import aiohttp
import json
from datetime import datetime
import time
import random
import string

# 只在本地開發時載入 .env（避免在 Render 重複讀取）
if os.getenv("RENDER") is None: # Render 上會內建設定 RENDER=True
    load_dotenv()

line_bot_api = LineBotApi(os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))
parser = WebhookParser(os.getenv("LINE_CHANNEL_SECRET"))

async def handle_user_message(body: bytes, x_line_signature: str): # 接收 user 訊息
    events = parser.parse(body.decode("utf-8"), x_line_signature)
    for event in events: # 判斷不同訊息類型
        if isinstance(event, FollowEvent): # 加入好友
            await add_new_user(event)
        else:
            user_id = event.source.user_id
            # 確認使用者是否已存在 db
            if await check_user_in_db(user_id) == False: # 還沒加入 db
                await add_new_user(event)
            if isinstance(event, PostbackEvent): # 手動切換 AI/真人客服
                mode = event.postback.data
                reply_text = await switch_mode(user_id, mode, "manual") # 記錄這次和下次訊息的客服模式
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text=reply_text)
                )
            elif isinstance(event, MessageEvent) and isinstance(event.message, TextMessage): # 處理一般文字訊息
                await chat_message(event, user_id)
    return {"status": "ok"}

async def show_loading(user_id): # 顯示訊息 loading 效果
    async with aiohttp.ClientSession() as session:
        headers = {
            "Authorization": f"Bearer {os.getenv('LINE_CHANNEL_ACCESS_TOKEN')}",
            "Content-Type": "application/json"
        }
        payload = {
            "chatId": user_id,
            "loadingSeconds": 60
        }
        await session.post("https://api.line.me/v2/bot/chat/loading/start", headers=headers, json=payload)

async def check_user_in_db(user_id): # 確認使用者是否已存在 db
    return await chat_model.check_user_is_existed(user_id)

async def add_new_user(event): # 加入好友
    user_id = event.source.user_id
    profile = line_bot_api.get_profile(user_id)
    display_name = profile.display_name
    picture_url = profile.picture_url
    await chat_model.add_new_user(user_id, display_name, picture_url)

async def switch_mode(user_id, new_chat_mode, chanege_by): # 切換 AI/真人客服
    reply_text = ""
    if new_chat_mode == "human":
        if chanege_by == "manual":
            reply_text = "已切換為【真人客服】，請輸入您想詢問的問題，並稍候真人客服為您服務..."
        else:
            reply_text = "已切換為【真人客服】，請稍候真人客服為您服務..."
    elif new_chat_mode == "ai":
        reply_text = "已切換為【AI客服】，歡迎詢問問題"

    # 檢查 user 前一次的客服模式
    user_profile = await chat_model.get_user_profile(user_id)
    # 客服模式有變化，才做 db update
    if user_profile["now_chat_mode"] != new_chat_mode or user_profile["last_chat_mode"] != user_profile["now_chat_mode"]:
        await chat_model.switch_chat_mode(new_chat_mode, user_id, user_profile["now_chat_mode"], chanege_by)
    return reply_text

async def chat_message(event, user_id): # 處理一般文字訊息
    user_query = event.message.text # 使用者輸入的問題
    # 判斷使用者目前客服狀態 (AI or 真人)
    user_profile = await chat_model.get_user_profile(user_id)
    if user_profile["now_chat_mode"] == "human": # 真人客服
        if user_profile["last_chat_mode"] == "ai": # 上次是 AI 客服
            if user_profile["change_by"] == "manual": # 是手動切換為真人客服, 表示是第一次發送訊息
                notify_code = get_notify_code() # 取得唯一通知碼
                await call_human_support(user_profile, user_query, notify_code) # 發送通知給真人客服
        await switch_mode(user_id, "human", "system") # 記錄這次和下次訊息的客服模式

    elif user_profile["now_chat_mode"] == "ai": # AI 客服
        await call_ai_assistant(event, user_id, user_profile, user_query)

def get_notify_code():
    # 產生唯一通知碼
    timestamp = int(time.time())  # 取得當前時間戳（秒）
    rand_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4)) # 隨機 4 碼英數組合
    notify_code = f"{timestamp}-{rand_part}"
    return notify_code

def get_current_time(): # 取得現在時間
    now = datetime.now()
    return now.strftime("%Y-%m-%d %H:%M")

async def call_human_support(user_profile, user_query, notify_code): # 通知真人客服
    # 通知真人客服
    client_ids = os.getenv("LINE_CLIENT_ID")
    notify_text = f"""🔔 [真人客服通知]
使用者：{user_profile["display_name"]}
時間：{get_current_time()}
訊息代碼：{notify_code}
使用者訊息：{user_query}"""
    for client_id in client_ids.split(","):
        message = TextSendMessage(text=notify_text)
        line_bot_api.push_message(client_id, message)

async def call_ai_assistant(event, user_id, user_profile, user_query):
    # 顯示 loading 動畫
    await show_loading(user_id)

    session_id = str(uuid.uuid4()) # 對話 id

    # 重寫使用者問題
    rewritten_query = await rewrite_chat_question(user_query)
    logger.info(f"對話{session_id}, 原問題: {user_query}, 重寫問題: {rewritten_query}")

    # function call 判斷是否需要 rag
    # prompt = [
    #     {
    #         "role": "user",
    #         "content": query
    #     }
    # ]
    # analyze_intent = await call_llm.call_gpt_analye_intent(prompt)
    # print("analyze_intent", analyze_intent)
    # related_data = []
    
    # rag
    analyze_intent = True # 先改成必定做 rag
    if analyze_intent:
        # 檢索
        # 轉向量並比對 db 相關資料 (取前 n)
        related_data = await rag_tool.search_with_rag(rewritten_query)

    rag_data = ""
    for i in range(len(related_data)):
        rag_data += f"問題{i+1}: {related_data[i]['question']}\n答案: {related_data[i]['answer']}\n"
    # 組 prompt
    chatbot_messages = [
        {
            "role": "user",
            # 例行 prompt + 檢索到的資料 + 語言
            "content": chatbot_prompt["instruction"] +
            chatbot_prompt["constraints"] +
            chatbot_prompt["input"].format(rewritten_query=rewritten_query, rag_data=rag_data) +
            chatbot_prompt["language"]
        }
    ]
    # call gpt
    reply_message, can_answer = await call_llm.call_gpt_generate_chat_response(chatbot_messages)
    # 判斷 AI 是否能夠正確回答
    if can_answer == False: # 無法正確回答
        reply_text = await switch_mode(user_id, "human", "system") # 記錄這次和下次訊息的客服模式
        # 通知真人客服
        notify_code = get_notify_code() # 取得唯一通知碼
        notify_text = f"訊息代碼: {notify_code}"
        await call_human_support(user_profile, user_query, notify_code) # 通知真人客服
        reply_message += "\n" + reply_text + "\n" + notify_text # 組成回傳訊息
    else:
        await switch_mode(user_id, "ai", "system") # 記錄這次和下次訊息的客服模式
    reply_message += "\n(此回覆由 AI 生成)" # AI 回覆訊息最後固定加上
    logger.info(f"對話{session_id}, 傳送問題: {chatbot_messages}, 傳送回覆: {reply_message}")
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_message))

async def rewrite_chat_question(query):
    # 使用 GPT 重寫使用者問題
    rewrite_messages = [
        {
            "role": "user",
            "content": rewrite_prompt["instruction"] + rewrite_prompt["constraints"] + rewrite_prompt["input"].format(query=query)
        }
    ]
    return await call_llm.call_gpt(rewrite_messages)