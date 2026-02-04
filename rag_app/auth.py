"""
Azure AD Authentication Module

Validates Azure AD JWT tokens and extracts user identity and group memberships
for permission-aware document access.
"""
import os
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from jwt import PyJWKClient
from functools import lru_cache

from rag_app.config import TENANT_ID

# Azure AD configuration
AZURE_AD_AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
AZURE_AD_JWKS_URI = f"https://login.microsoftonline.com/{TENANT_ID}/discovery/v2.0/keys"

# Expected audience - should be your API's Application ID URI or client ID
AZURE_AD_AUDIENCE = os.getenv("AZURE_AD_API_CLIENT_ID", os.getenv("CLIENT_ID"))

# Security scheme for FastAPI
security = HTTPBearer(auto_error=False)


class User:
    """Represents an authenticated Azure AD user."""
    
    def __init__(self, user_id: str, email: Optional[str], name: Optional[str], groups: list[str]):
        self.user_id = user_id
        self.email = email
        self.name = name
        self.groups = groups  # List of group IDs the user belongs to
    
    @property
    def all_principals(self) -> list[str]:
        """Returns all principal IDs (user ID + group IDs) for security filtering."""
        return [self.user_id] + self.groups


@lru_cache(maxsize=1)
def get_jwks_client():
    """Get cached JWKS client for token validation."""
    return PyJWKClient(AZURE_AD_JWKS_URI)


def decode_token(token: str) -> dict:
    """
    Decode and validate an Azure AD JWT token.
    
    Validates:
    - Signature using Azure AD's public keys
    - Issuer (Azure AD tenant)
    - Audience (this API)
    - Expiration
    """
    try:
        jwks_client = get_jwks_client()
        signing_key = jwks_client.get_signing_key_from_jwt(token)
        
        decoded = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            audience=AZURE_AD_AUDIENCE,
            issuer=f"https://login.microsoftonline.com/{TENANT_ID}/v2.0",
            options={
                "verify_exp": True,
                "verify_aud": True,
                "verify_iss": True,
            }
        )
        return decoded
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.InvalidAudienceError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token audience"
        )
    except jwt.InvalidIssuerError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token issuer"
        )
    except jwt.PyJWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}"
        )


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[User]:
    """
    FastAPI dependency to get the current authenticated user.
    
    Extracts user identity and group memberships from Azure AD token.
    Returns None if no token is provided (enables optional auth).
    """
    if credentials is None:
        return None
    
    token = credentials.credentials
    decoded = decode_token(token)
    
    # Extract user info from token claims
    user_id = decoded.get("oid") or decoded.get("sub")  # Object ID or Subject
    email = decoded.get("preferred_username") or decoded.get("email")
    name = decoded.get("name")
    
    # Extract group memberships
    # Note: Groups must be configured to be included in token claims in Azure AD app registration
    groups = decoded.get("groups", [])
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token missing user identifier"
        )
    
    return User(user_id=user_id, email=email, name=name, groups=groups)


async def require_auth(
    user: Optional[User] = Depends(get_current_user)
) -> User:
    """
    FastAPI dependency that requires authentication.
    Raises 401 if user is not authenticated.
    """
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"}
        )
    return user
