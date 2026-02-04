from langchain_openai import OpenAIEmbeddings
from rag_app.config import *

embeddings = OpenAIEmbeddings(
    api_key=OPENAI_API_KEY,
    model=OPENAI_EMBEDDING_MODEL
)
