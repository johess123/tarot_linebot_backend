from openai import OpenAI
import os

openai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
embedding_model = os.getenv("EMBEDDING_MODEL")

def get_embedding(text: str):
    res = openai.embeddings.create(input=text, model=embedding_model)
    return res.data[0].embedding
