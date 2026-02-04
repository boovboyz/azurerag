import os
import tempfile
import requests
from msal import ConfidentialClientApplication, PublicClientApplication
import webbrowser
from rag_app.config import *
from dotenv import load_dotenv

load_dotenv()  # This loads variables from .env into os.environ
TENANT_ID = os.getenv("TENANT_ID")
CLIENT_ID =  os.getenv("CLIENT_ID")
api_key = os.getenv("API_KEY")

GRAPH_SCOPE = ["https://graph.microsoft.com/.default"]

# SCOPES = [
#     "User.Read",
#     "Sites.Read.All",
#     "Files.Read"
# ]

# authority = f"https://login.microsoftonline.com/{TENANT_ID}"

def get_token():
    # app = PublicClientApplication(
    #     client_id=CLIENT_ID,
    #     authority=authority
    # )

    # flow = app.initiate_auth_code_flow(
    #     scopes=SCOPES,
    #     redirect_uri="http://localhost:8400"
    # )

    # webbrowser.open(flow["auth_uri"])

    # redirect_response = input("Paste the FULL redirected URL here:\n")

    # token = app.acquire_token_by_auth_code_flow(
    #     flow,
    #     redirect_response
    # )

    # if "access_token" not in token:
    #     raise RuntimeError(token)

    # return token["access_token"]

    app = ConfidentialClientApplication(
        CLIENT_ID,
        authority=f"https://login.microsoftonline.com/{TENANT_ID}",
        client_credential=CLIENT_SECRET
    )
    return app.acquire_token_for_client(scopes=GRAPH_SCOPE)["access_token"]

def list_files():
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}
    url = f"https://graph.microsoft.com/v1.0/drives/{DRIVE_ID}/items/{FOLDER_ID}/children"
    return requests.get(url, headers=headers).json()["value"]

def download_file(file_id, filename):
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}
    url = f"https://graph.microsoft.com/v1.0/drives/{DRIVE_ID}/items/{file_id}/content"
    r = requests.get(url, headers=headers)

    path = os.path.join(tempfile.gettempdir(), filename)
    with open(path, "wb") as f:
        f.write(r.content)
    return path
