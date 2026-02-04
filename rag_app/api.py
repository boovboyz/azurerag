"""
FastAPI Application

Provides both authenticated and unauthenticated endpoints for RAG queries.
The secure endpoint applies document-level security based on Azure AD groups.
"""
from typing import Optional
from fastapi import FastAPI, Depends, Query
from fastapi.middleware.cors import CORSMiddleware

from rag_app.rag_chain import rag_chain, invoke_secure
from rag_app.auth import get_current_user, require_auth, User

app = FastAPI(
    title="SharePoint RAG API",
    description="Query SharePoint documents with AI - supports permission-aware access",
    version="2.0.0"
)

# CORS middleware for browser-based clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/ask")
def ask(question: str = Query(..., description="Your question about the documents")):
    """
    Query documents without authentication (backward compatible).
    
    WARNING: This endpoint does NOT apply permission filtering.
    All indexed documents are searchable.
    """
    return {
        "answer": rag_chain.invoke(question),
        "authenticated": False,
        "warning": "No permission filtering applied"
    }


@app.post("/ask/secure")
def ask_secure(
    question: str = Query(..., description="Your question about the documents"),
    user: User = Depends(require_auth)
):
    """
    Query documents with Azure AD authentication and permission filtering.
    
    Only returns answers from documents the authenticated user has access to
    based on their SharePoint permissions.
    
    Requires: Bearer token from Azure AD in Authorization header.
    """
    # Use the user's principals (user ID + group IDs) for security filtering
    answer = invoke_secure(question, user.all_principals)
    
    return {
        "answer": answer,
        "authenticated": True,
        "user": {
            "id": user.user_id,
            "email": user.email,
            "name": user.name,
            "groups_count": len(user.groups)
        }
    }


@app.get("/me")
def get_me(user: User = Depends(require_auth)):
    """
    Get information about the authenticated user.
    Useful for testing authentication setup.
    """
    return {
        "user_id": user.user_id,
        "email": user.email,
        "name": user.name,
        "groups": user.groups,
        "all_principals": user.all_principals
    }


@app.get("/health")
def health():
    """Health check endpoint."""
    return {"status": "healthy", "version": "2.0.0"}

