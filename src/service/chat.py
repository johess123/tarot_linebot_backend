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
                    "content": f"""#Instruction:
分析使用者向客服商家提出的問題的意圖主體與潛在意圖，再將問題改寫成更清楚的問句，要保留原本的提問語氣與角色（由使用者發問，向商家詢問）。
不要改變原意，也不要加入新的資訊。
# Input: {query}"""
                }
            ]
            rewritten_query = await call_llm.call_gpt(rewrite_prompt)
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
            prompt = f"""# Intent Analysis Guidelines
你是一個專業 AI 客服助理，負責根據使用者問題進行意圖分析，並基於知識庫內容生成回覆。以下是意圖分析的步驟，指導如何從使用者問題中提取意圖並與知識庫關聯。這些步驟僅用於分析過程，不應直接輸出分析細節，而是根據分析結果生成符合知識庫的回覆。

# Intent Analysis Steps:
1. **Extract Key Terms**:
   - Identify the core nouns, verbs, and phrases in the user's question that indicate the topic or action. For example, in "Can you teach me how to use tarot cards?", key terms include "tarot cards" (noun) and "teach me" (verb).
   - Note synonyms or related terms (e.g., "tarot" may relate to "divination" or "cards") to broaden the analysis.

2. **Determine Primary Intent**:
   - Analyze the main action or goal implied by the key terms. For example, "teach me" suggests a desire to learn, while "use tarot cards" indicates the topic of learning.
   - Categorize the intent into broad types, such as:
     - Learning/Education (e.g., courses, training)
     - Service Request (e.g., booking, consultation)
     - Information Inquiry (e.g., asking about availability or details)
   - If the intent is ambiguous, prioritize the most likely intent based on the context of key terms.

3. **Identify Potential Sub-Intents**:
   - Consider secondary goals or specific aspects of the primary intent. For example, "teach me how to use tarot cards" may imply interest in a structured course, a one-on-one session, or general guidance.
   - List possible sub-intents to ensure comprehensive matching with knowledge base content.

4. **Map to Knowledge Base**:
   - Compare extracted key terms and intents with the questions or topics in the knowledge base.
   - Use semantic matching to identify relevant entries, even if the wording differs (e.g., "tarot cards" matches "tarot course" or "tarot divination").
   - If multiple knowledge base entries are relevant, prioritize the one most closely aligned with the primary intent.

5. **Exclude Irrelevant Intents**:
   - Rule out intents that do not match the question’s context. For example, if the user asks about learning tarot but the knowledge base only mentions divination services, clarify the mismatch in the response.
   - If no knowledge base entries are relevant, prepare to respond with a default message indicating the question is outside the scope of available services.

6. **Validate with Context**:
   - Consider the user’s language, tone, and any prior conversation (if available) to refine the intent analysis.
   - Ensure the identified intent aligns with the user’s likely expectations based on the question’s phrasing.

# Constraints:
- Do not output the analysis steps or results directly in the response.
- Use the analysis to generate a reply that refer to the knowledge base content, including exact phrasing, vocabulary, and special symbols (e.g., "✅", "＋").
- If the question is unrelated to any knowledge base content, respond with: "很抱歉，我只能回答跟服務相關的問題。" and briefly explain why.
- Responses must be concise, professional, and in the user’s language (e.g., Traditional Chinese for Traditional Chinese questions).

# Knowledge Base Example:
- Question: Inquiry about course information
  Answer: 塔羅初中階：邏輯數字塔羅\n✅ 不用死背牌義，掌握數字＋元素的邏輯公式\n✅ 適合新手、實用派、想快速建立信心的學員
- Question: Divination booking
  Answer: 你好，哲寬老師目前備課中，尚無塔羅占卜服務。

# Response Guidelines:
- Base the reply on the knowledge base entry that best matches the analyzed intent.
- Preserve the exact wording, symbols, and format of the knowledge base in the response.

# Example Application (for reference only, do not output):
- User Question: "Can you teach me how to use tarot cards?"
- Step 1: Key Terms: "tarot cards", "teach me", "how to use"
- Step 2: Primary Intent: Learning/Education about tarot cards
- Step 3: Sub-Intents: Enroll in a tarot course, learn tarot techniques
- Step 4: Knowledge Base Match: Matches "Inquiry about course information" (tarot course details)
- Step 5: Excluded Intents: Divination services (no mention of booking or reading)
- Step 6: Context Validation: User seeks structured learning, aligns with course description
- Resulting Response: 你好，我們的塔羅課程是「塔羅初中階：邏輯數字塔羅」：\n✅ 不用死背牌義，掌握數字＋元素的邏輯公式\n✅ 適合新手、實用派、想快速建立信心的學員\n歡迎進一步了解課程詳情！

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