from src.ToolsApi import call_llm, rag_tool
from src.models import chat as chat_model
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
            rewrite_prompt = [
                {
                    "role": "user",
                    "content": f"請重寫以下問題以使其更清晰：{query}"
                }
            ]
            rewritten_query = await call_llm.call_gpt(rewrite_prompt)

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
            analyze_intent = True # 先改成必定 rag
            if analyze_intent:
                # rag
                # 1. 檢索
                # 轉向量並比對 db 相關資料 (取前 n)
                related_data = await rag_tool.search_with_rag(rewritten_query)
                count = 1
                for i in related_data:
                    count += 1
                # 2. 組 prompt
            #    a. 例行 prompt (語調, query)
            prompt = f"""#Instruction:
你是一個專業 AI 客服助理，你會基於知識庫檢索到的資料回答使用者問題。
# Constraints:
    1. 知識庫檢索的資料是多組問答對，你只能根據知識庫的內容回答。
    2. 如果使用者問題與任何一組以上問答內容相關，就根據這些資料內容回答。
    3. 如果使用者的問題與知識庫所有問答都不相關，才回答：「很抱歉，我只能回答跟服務相關的問題」。
# Input:
    ## 使用者問題: {rewritten_query}
    ## 知識庫檢索資料: """
            #    b. 檢索到的資料
            rag_data = ""
            for i in range(len(related_data)):
                rag_data += f"問題{i+1}: {related_data[i]['question']}\n答案: {related_data[i]['answer']}\n"
            language = "#Language: 根據使用者使用的語言回答"
            #    c. 組 prompt
            prompt += rag_data + language
            messages = [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
            print(f"對話{session_id}, 傳送問題: ", messages)
            # call gpt
            reply = await call_llm.call_gpt(messages)
            print(f"對話{session_id}, 傳送回覆: ", reply)
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))
    return {"status": "ok"}