from fastapi import FastAPI
from rag_app.rag_chain import rag_chain

app = FastAPI()

@app.post("/ask")
def ask(question: str):
    return {
        "answer": rag_chain.invoke(question)
    }
