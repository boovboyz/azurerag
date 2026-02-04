from azure.core.credentials import AzureKeyCredential
from azure.search.documents.indexes import SearchIndexClient
from rag_app.config import *

def reset_index():
    client = SearchIndexClient(AZURE_SEARCH_ENDPOINT, AzureKeyCredential(AZURE_SEARCH_KEY))
    print(f"Deleting index: {AZURE_SEARCH_INDEX}...")
    try:
        client.delete_index(AZURE_SEARCH_INDEX)
        print("Index deleted successfully.")
    except Exception as e:
        print(f"Warning: Could not delete index (it might not exist): {e}")

if __name__ == "__main__":
    reset_index()
