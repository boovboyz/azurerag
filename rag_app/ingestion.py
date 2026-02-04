from langchain_core.documents import Document
from rag_app.sharepoint_loader import list_files, download_file, get_file_permissions
from rag_app.document_parser import extract_text
from rag_app.chunking import chunk_text
from rag_app.azure_search import vector_store

def ingest():
    """
    Ingest documents from SharePoint into Azure Search.
    Now includes fetching and storing document permissions for security filtering.
    """
    docs = []
    total_files = 0
    
    print("Starting permission-aware ingestion...")

    for f in list_files():
        if "file" not in f:
            continue
        
        total_files += 1
        file_id = f["id"]
        file_name = f["name"]
        
        print(f"Processing: {file_name}")

        # Download and extract text
        path = download_file(file_id, file_name)
        text = extract_text(path)
        
        # Fetch permissions for security filtering
        allowed_principals = get_file_permissions(file_id)
        print(f"  - Found {len(allowed_principals)} allowed principals")

        # Chunk and create documents with permission metadata
        for chunk in chunk_text(text):
            docs.append(
                Document(
                    page_content=chunk,
                    metadata={
                        "source": file_name,
                        "file_id": file_id,
                        "allowed_groups": allowed_principals  # For security filtering
                    }
                )
            )
    
    print(f"\nIngesting {len(docs)} chunks from {total_files} files...")
    vector_store.add_documents(docs)
    print("Ingestion complete!")

