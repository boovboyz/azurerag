import os
import sys
import urllib.parse
import requests
from msal import ConfidentialClientApplication, PublicClientApplication
import webbrowser
from dotenv import load_dotenv

load_dotenv()

# =========================
# CONFIG (env vars)
# =========================
TENANT_ID = os.getenv("TENANT_ID")
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

SCOPES = [
    "User.Read",
    "Sites.Read.All",
    "Files.Read"
]

authority = f"https://login.microsoftonline.com/{TENANT_ID}"

if not all([TENANT_ID, CLIENT_ID]):
    print("❌ Missing TENANT_ID, CLIENT_ID, or CLIENT_SECRET")
    sys.exit(1)

GRAPH_SCOPE = ["https://graph.microsoft.com/.default"]

# =========================
# AUTH
# =========================
def get_token():

    app = ConfidentialClientApplication(
        CLIENT_ID,
        authority=f"https://login.microsoftonline.com/{TENANT_ID}",
        client_credential=CLIENT_SECRET,
    )
    return app.acquire_token_for_client(
        scopes=["https://graph.microsoft.com/.default"]
    )["access_token"]

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

# =========================
# HELPERS
# =========================
def graph_get(url, token):
    r = requests.get(url, headers={"Authorization": f"Bearer {token}"})
    if not r.ok:
        raise RuntimeError(f"{r.status_code} {r.text}")
    return r.json()

# =========================
# DISCOVERY LOGIC
# =========================
def discover_ids(sharepoint_folder_url):
    token = get_token()
    parsed = urllib.parse.urlparse(sharepoint_folder_url)

    hostname = parsed.hostname
    path_parts = parsed.path.strip("/").split("/")

    # Example:
    # sites/HR/Shared Documents/Folder/Subfolder
    if path_parts[0] != "sites":
        raise ValueError("Only /sites/<site-name> URLs are supported")

    site_name = path_parts[1]
    folder_path = "/".join(path_parts[2:])

    # 1️⃣ Get SITE_ID
    site = graph_get(
        f"https://graph.microsoft.com/v1.0/sites/{hostname}:/sites/{site_name}",
        token,
    )
    site_id = site["id"]

    # 2️⃣ Get DRIVE_ID (Documents library)
    drives = graph_get(
        f"https://graph.microsoft.com/v1.0/sites/{site_id}/drives",
        token,
    )
    drive = next(d for d in drives["value"] if d["name"] == "Documents")
    drive_id = drive["id"]

    # 3️⃣ Get FOLDER_ID by path
    folder = graph_get(
        f"https://graph.microsoft.com/v1.0/drives/{drive_id}/root:/{folder_path}",
        token,
    )
    folder_id = folder["id"]

    return site_id, drive_id, folder_id

# =========================
# CLI
# =========================
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage:")
        print("  python test.py <sharepoint-folder-url>")
        sys.exit(1)

    url = sys.argv[1]
    site_id, drive_id, folder_id = discover_ids(url)

    print("\n✅ Discovered SharePoint IDs:\n")
    print(f"SITE_ID={site_id}")
    print(f"DRIVE_ID={drive_id}")
    print(f"FOLDER_ID={folder_id}")
