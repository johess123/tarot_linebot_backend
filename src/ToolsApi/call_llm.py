import os
from openai import OpenAI
from src.ToolsApi.tools import all_tools
import json
import os
from dotenv import load_dotenv

# 只在本地開發時載入 .env（避免在 Render 重複讀取）
if os.getenv("RENDER") is None:  # Render 上會內建設定 RENDER=True
    load_dotenv()

openai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
llm_model = os.getenv("LLM_MODEL")

async def call_gpt(prompt: dict) -> str: # gpt 生成回覆
    res = openai.chat.completions.create(
        model=llm_model,
        messages=prompt,
        temperature=0.5
    )
    return res.choices[0].message.content

async def call_gpt_analye_intent(prompt: dict) -> str: # 分析使用者問題意圖
    res = openai.chat.completions.create(
        model=llm_model,
        messages=prompt,
        tools=all_tools,
        tool_choice={
            "type": "function",
            "function": {
                "name": "analyze_intent"
            }
        }
    )
    return json.loads(res.choices[0].message.tool_calls[0].function.arguments).get("rag")
