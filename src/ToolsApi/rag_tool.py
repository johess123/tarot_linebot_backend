from src.ToolsApi import call_embedding
from src.models import chat as chat_model

async def search_with_rag(query: str) -> str:
    embedding = call_embedding.get_embedding(query)
    result = await chat_model.query_service_by_vector(embedding)
    return result