"""
RAG Chain Module

Provides both unsecured and permission-aware RAG chains.
The secure version applies Azure Search security filters based on user groups.
"""
from typing import Optional
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda

from rag_app.azure_search import vector_store
from rag_app.config import *

# LLM
llm = ChatOpenAI(
    api_key=OPENAI_API_KEY,
    model=OPENAI_CHAT_MODEL,
    temperature=0.2
)

# Default retriever (no security filtering)
retriever = vector_store.as_retriever(k=5)

# Prompt
prompt = ChatPromptTemplate.from_template(
    """
You are a helpful assistant.
Answer the question ONLY using the context below.
If the answer is not in the context, say "I don't know".

Context:
{context}

Question:
{question}
"""
)

# Default RAG chain (LCEL) - no security filtering
rag_chain = (
    {
        "context": retriever,
        "question": RunnablePassthrough()
    }
    | prompt
    | llm
    | StrOutputParser()
)


def create_secure_retriever(user_principals: list[str], k: int = 5):
    """
    Create a retriever with security filtering based on user's principal IDs.
    
    Uses Azure Search's search.in() filter to only return documents where
    the allowed_groups field contains at least one of the user's principals.
    
    Args:
        user_principals: List of user ID and group IDs the user belongs to
        k: Number of documents to retrieve
    
    Returns:
        A retriever that only returns documents the user has access to
    """
    if not user_principals:
        # No principals = no access
        return vector_store.as_retriever(k=k, filters="1 eq 0")  # Always false filter
    
    # Build OData filter: search.in(allowed_groups, 'id1,id2,id3', ',')
    # This returns documents where allowed_groups contains any of the provided IDs
    principals_str = ",".join(user_principals)
    filter_expr = f"allowed_groups/any(g: search.in(g, '{principals_str}', ','))"
    
    return vector_store.as_retriever(k=k, filters=filter_expr)


def create_secure_rag_chain(user_principals: list[str]):
    """
    Create a permission-aware RAG chain for a specific user.
    
    Args:
        user_principals: List of user ID and group IDs (from Azure AD token)
    
    Returns:
        A RAG chain that only retrieves documents the user has access to
    """
    secure_retriever = create_secure_retriever(user_principals)
    
    return (
        {
            "context": secure_retriever,
            "question": RunnablePassthrough()
        }
        | prompt
        | llm
        | StrOutputParser()
    )


def invoke_secure(question: str, user_principals: Optional[list[str]] = None) -> str:
    """
    Invoke RAG with optional security filtering.
    
    Args:
        question: The user's question
        user_principals: If provided, applies security filtering
    
    Returns:
        The generated answer
    """
    if user_principals:
        chain = create_secure_rag_chain(user_principals)
    else:
        chain = rag_chain
    
    return chain.invoke(question)

