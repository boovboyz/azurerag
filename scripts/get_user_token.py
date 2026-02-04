import os
import sys
import json
from msal import PublicClientApplication
from dotenv import load_dotenv

# Add parent directory to path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
load_dotenv()

TENANT_ID = os.getenv("TENANT_ID")
# Use the same Client ID as the API assumes for audience validation
CLIENT_ID = os.getenv("AZURE_AD_API_CLIENT_ID") or os.getenv("CLIENT_ID")

if not CLIENT_ID or not TENANT_ID:
    print("Error: TENANT_ID or CLIENT_ID not found in .env")
    sys.exit(1)

# Scopes required by the API
# If the API exposes a scope like "api://<client-id>/access_as_user", use that.
# For simple testing with same client ID, we can often use ".default" or "User.Read".
# Ideally, for a custom API, you define a scope.
# Checking commonly used scopes:
SCOPES = ["User.Read", "Files.Read"] 

def get_token():
    authority = f"https://login.microsoftonline.com/{TENANT_ID}"
    
    app = PublicClientApplication(
        client_id=CLIENT_ID,
        authority=authority
    )
    
    print(f"Attempting to acquire token for client: {CLIENT_ID}")
    
    # Try to get token interactively (opens browser)
    result = app.acquire_token_interactive(scopes=SCOPES)
    
    if "access_token" in result:
        print("\nSUCCESS! Here is your Bearer token:\n")
        print(result["access_token"])
        print("\nUse it in your request header:")
        print(f'Authorization: Bearer {result["access_token"]}')
        
        # Decode specific claims to verify groups
        if "id_token_claims" in result:
            claims = result["id_token_claims"]
            print("\nToken Claims Summary:")
            print(f"User: {claims.get('name')} ({claims.get('preferred_username')})")
            print(f"Groups: {len(claims.get('groups', []))} groups found")
            if "groups" not in claims:
                print("WARNING: No 'groups' claim found. Configuring Azure AD 'Token Configuration' is required for RAG permissions.")
    else:
        print("\nError acquiring token:")
        print(result.get("error"))
        print(result.get("error_description"))

if __name__ == "__main__":
    get_token()
