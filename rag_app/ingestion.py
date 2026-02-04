from langchain_core.documents import Document
from rag_app.sharepoint_loader import list_files, download_file
from rag_app.document_parser import extract_text
from rag_app.chunking import chunk_text
from rag_app.azure_search import vector_store

def ingest():
    docs = []

    for f in list_files():
        if "file" not in f:
            continue

        path = download_file(f["id"], f["name"])
        text = extract_text(path)

        for chunk in chunk_text(text):
            docs.append(
                Document(
                    page_content=chunk,
                    metadata={
                        "source": f["name"],
                        "file_id": f["id"]
                    }
                )
            )

    vector_store.add_documents(docs)
