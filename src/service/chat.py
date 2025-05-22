from src.ToolsApi import call_llm, rag_tool
from src.config.prompt import rewrite_prompt, chatbot_prompt
from linebot import LineBotApi, WebhookParser
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import os
import uuid
from dotenv import load_dotenv

# 只在本地開發時載入 .env（避免在 Render 重複讀取）
if os.getenv("RENDER") is None:  # Render 上會內建設定 RENDER=True
    load_dotenv()

line_bot_api = LineBotApi(os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))
parser = WebhookParser(os.getenv("LINE_CHANNEL_SECRET"))

async def handle_user_message(body: bytes, x_line_signature: str): # 接收 user 訊息
    events = parser.parse(body.decode("utf-8"), x_line_signature)
    for event in events:
        if isinstance(event, MessageEvent) and isinstance(event.message, TextMessage):
            session_id = str(uuid.uuid4())
            query = event.message.text
            # 使用 GPT 重寫使用者問題
            rewrite_messages = [
                {
                    "role": "user",
                    "content": rewrite_prompt["instruction"] + rewrite_prompt["constraints"] + rewrite_prompt["input"].format(query=query)
                }
            ]
            rewritten_query = await call_llm.call_gpt(rewrite_messages)
            print(f"對話{session_id}, 原問題: {query}, 重寫問題: ", rewritten_query)

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
            print(f"對話{session_id}, 傳送問題: ", chatbot_messages)
            # call gpt
            reply = await call_llm.call_gpt(chatbot_messages)
            print(f"對話{session_id}, 傳送回覆: ", reply)
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))
    return {"status": "ok"}