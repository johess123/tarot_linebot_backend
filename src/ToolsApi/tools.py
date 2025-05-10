all_tools = [
    {
        "type": "function",
        "function": {
            "name": "analyze_intent",
            "description": "判斷使用者問題的意圖是否是想詢問提供哪些服務，或想詢問服務內容，如果有關，回傳 rag: true，不相關則回傳 rag: false。",
            "parameters": {
                "type": "object",
                "properties": {
                    "rag": {
                        "type": "boolean",
                        "description": "如果使用者問題的意圖是想詢問提供哪些服務，或是想詢問服務內容，則為 true；如果不相關，則為 false。"
                    }
                },
                "required": ["rag"]
            }
        }
    },
]