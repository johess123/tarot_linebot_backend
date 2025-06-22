all_tools = [
    {
        "type": "function",
        "function": {
            "name": "generate_response",
            "description": "根據使用者問題和知識庫內容生成回覆，並判斷是否能夠正確回答",
            "parameters": {
                "type": "object",
                "properties": {
                    "reply_message": {
                        "type": "string",
                        "description": "生成的回覆訊息。若無法回答則固定回傳「很抱歉，我只能回答跟服務相關的問題。」"
                    },
                    "can_answer": {
                        "type": "boolean",
                        "description": "是否能夠根據知識庫正確回答使用者問題"
                    }
                },
                "required": ["reply_message", "can_answer"],
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "analyze_intent",
            "description": "判斷使用者問題的意圖是否是想詢問提供哪些服務，或想詢問服務內容，如果有關，回傳 rag: true，不相關則回傳 rag: false。",
            "strict": True,
            "parameters": {
                "type": "object",
                "properties": {
                    "rag": {
                        "type": "boolean",
                        "description": "如果使用者問題的意圖是想詢問提供哪些服務，或是想詢問服務內容，則為 true；如果不相關，則為 false。"
                    }
                },
                "required": ["rag"],
                "additionalProperties": False
            }
        }
    }
]