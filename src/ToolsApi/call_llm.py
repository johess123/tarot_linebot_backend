import os
from openai import OpenAI
from src.ToolsApi.tools import all_tools
import json
import os

openai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
llm_model = os.getenv("LLM_MODEL")

async def call_gpt(prompt: dict) -> str:
    res = openai.chat.completions.create(
        model=llm_model,
        messages=prompt
    )
    return res.choices[0].message.content

async def call_gpt_analye_intent(prompt: dict) -> str:
    
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
