# SharePoint RAG with Azure AI Search

A Retrieval-Augmented Generation (RAG) application that enables Q&A over SharePoint documents using Azure AI Search and OpenAI.

## Architecture

```
SharePoint → MS Graph API → Document Parser → Text Chunking → Azure AI Search
                                                                    ↓
                        User Query → FastAPI → RAG Chain (LangChain + GPT)
```

## Features

- **SharePoint Integration**: Connects to SharePoint via Microsoft Graph API
- **Multi-format Support**: Parses PDF, DOCX, PPTX, and XLSX files
- **Vector Search**: Uses Azure AI Search for semantic document retrieval
- **RAG Pipeline**: LangChain-based RAG with OpenAI GPT models

## Setup

### Prerequisites

- Python 3.10+
- Azure AI Search service
- OpenAI API key
- Azure AD app registration with SharePoint permissions

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/boovboyz/azurerag.git
   cd azurerag
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

4. Discover SharePoint IDs:
   ```bash
   python test.py "https://yourtenant.sharepoint.com/sites/YourSite/Shared Documents/YourFolder"
   ```
   Copy the output SITE_ID, DRIVE_ID, and FOLDER_ID to your `.env` file.

### Usage

1. **Ingest documents** from SharePoint:
   ```bash
   python scripts/ingest_sharepoint.py
   ```

2. **Start the API server**:
   ```bash
   uvicorn rag_app.api:app --host 0.0.0.0 --port 8000
   ```

3. **Query your documents**:
   ```bash
   curl -X POST "http://localhost:8000/ask?question=What%20is%20in%20my%20documents"
   ```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/ask?question=<query>` | Query documents with natural language |

## Project Structure

```
├── rag_app/
│   ├── api.py              # FastAPI endpoints
│   ├── azure_search.py     # Azure AI Search vector store
│   ├── chunking.py         # Text splitting
│   ├── config.py           # Environment configuration
│   ├── document_parser.py  # PDF/DOCX/PPTX/XLSX parsing
│   ├── embeddings.py       # OpenAI embeddings
│   ├── ingestion.py        # Document ingestion pipeline
│   ├── rag_chain.py        # LangChain RAG pipeline
│   └── sharepoint_loader.py # SharePoint Graph API client
├── scripts/
│   └── ingest_sharepoint.py # Ingestion CLI
├── test.py                  # SharePoint ID discovery tool
├── requirements.txt
└── .env.example
```

## ⚠️ Security Note

This implementation does **not** maintain SharePoint document-level permissions. All indexed documents are accessible to anyone with API access. For production use, implement:

- User authentication on the API
- Document ACL storage in Azure Search
- Security filters at query time

## License

MIT
